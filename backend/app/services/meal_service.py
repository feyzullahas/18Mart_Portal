import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
import json

# Basit memory cache
class SimpleCache:
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
    
    def get(self, key: str) -> Optional[any]:
        if key in self._cache:
            item = self._cache[key]
            if datetime.now() < item["expires"]:
                return item["data"]
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, data: any, ttl_minutes: int = 60):
        self._cache[key] = {
            "data": data,
            "expires": datetime.now() + timedelta(minutes=ttl_minutes)
        }

cache = SimpleCache()

class MealService:
    OSEM_URL = "https://yemek.comu.edu.tr/"
    KYK_API_URL = "https://www.kykmenusu.com/api/getMeal/Canakkale"
    CACHE_TTL = 60  # 1 saat cache

    def _format_date(self, date_str: str) -> str:
        """Tarihi Türkçe formatla döndürür"""
        months = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
            5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
            9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
        }
        days = {
            0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe",
            4: "Cuma", 5: "Cumartesi", 6: "Pazar"
        }
        try:
            dt = datetime.strptime(date_str.split(" ")[0], "%Y-%m-%d")
            return f"{dt.day} {months[dt.month]} {dt.year} {days[dt.weekday()]}"
        except:
            return date_str

    def _get_today_turkish(self) -> str:
        """Bugünün tarihini Türkçe formatla döndürür"""
        months = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
            5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
            9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
        }
        days = {
            0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe",
            4: "Cuma", 5: "Cumartesi", 6: "Pazar"
        }
        now = datetime.now()
        return f"{now.day} {months[now.month]} {now.year} {days[now.weekday()]}"

    def _parse_meal_with_calorie(self, text: str) -> Dict:
        """'Yemek Adı (kalori)' formatını ayrıştırır"""
        match = re.match(r'^(.+?)\s*\((\d+)\)$', text.strip())
        if match:
            name = match.group(1).strip()
            calories = int(match.group(2))
            return {"name": name, "calories": calories}
        else:
            return {"name": text.strip(), "calories": None}

    def _parse_calorie_range(self, cal_str: str) -> int:
        """'650-850 kalori' formatından max kaloriyi çıkarır"""
        match = re.search(r'(\d+)[-–](\d+)', cal_str)
        if match:
            return int(match.group(2))
        return None

    async def get_osem_meals(self) -> List[Dict]:
        """ÖSEM web sitesinden tüm günlerin yemek listesini çeker (cached)"""
        # Cache'i devre dışı bırak - her zaman yeni veri çek
        print("ÖSEM: Yeni veri çekiliyor...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.OSEM_URL, timeout=15.0)
                
                if response.status_code != 200:
                    return self._get_fallback_osem()
                
                soup = BeautifulSoup(response.text, "html.parser")
                script = soup.find("script", string=re.compile(r"let response\s*="))
                
                if not script:
                    return self._get_fallback_osem()
                
                js = script.string
                
                match = re.search(
                    r"let response\s*=\s*(\{[\s\S]*?\})\s*let foodData",
                    js
                )
                
                if not match:
                    return self._get_fallback_osem()
                
                json_text = match.group(1)
                data = json.loads(json_text)
                
                today = datetime.today().strftime("%Y-%m-%d")
                
                all_days = []
                
                for idx, gun in enumerate(data.get("data", [])):
                    gun_tarihi = gun.get("startDate", "").split(" ")[0]
                    
                    meals = []
                    for yemek in gun.get("foodName", []):
                        meal = self._parse_meal_with_calorie(yemek)
                        meals.append(meal)
                    
                    total_cal = sum(m.get('calories', 0) or 0 for m in meals)
                    
                    all_days.append({
                        "date": self._format_date(gun.get("startDate", "")),
                        "dateRaw": gun_tarihi,
                        "menu": meals,
                        "total_calories": total_cal,
                        "isToday": gun_tarihi == today
                    })
                
                if not all_days:
                    return self._get_fallback_osem()
                
                print(f"ÖSEM: {len(all_days)} günün verisi çekildi")
                print(f"Bugün ({today}) için veri var mı: {any(day['isToday'] for day in all_days)}")
                
                return all_days
                
        except Exception as e:
            print(f"ÖSEM Scraping Hatası: {e}")
            return self._get_fallback_osem()
    
    def _get_fallback_osem(self) -> List[Dict]:
        today = datetime.today().strftime("%Y-%m-%d")
        return [{
            "date": self._get_today_turkish(),
            "dateRaw": today,
            "menu": [
                {"name": "Mercimek Çorbası", "calories": 130},
                {"name": "Orman Kebabı", "calories": 320},
                {"name": "Pirinç Pilavı", "calories": 260},
                {"name": "Ayran", "calories": 60}
            ],
            "total_calories": 770,
            "isToday": True
        }]

    async def get_kyk_meals(self) -> List[Dict]:
        """KYK Çanakkale API'sinden tüm günlerin yemek listesini çeker (cached)"""
        # Cache kontrol
        cached = cache.get("kyk_meals")
        if cached:
            print("KYK: Cache'den döndü")
            return cached
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.KYK_API_URL, timeout=15.0)
                
                if response.status_code != 200:
                    return self._get_fallback_kyk()
                
                data = response.json()
                
                # Bugünün tarihini Türkçe formatla al (API formatına uygun)
                today_turkish = self._get_today_turkish()
                
                # Verileri gün bazında grupla
                days_dict = {}
                
                for item in data:
                    date = item.get("date", "")
                    meal_type = item.get("meal_type", "")
                    menu = item.get("menu", [])
                    calories = item.get("calories", "")
                    
                    if date not in days_dict:
                        days_dict[date] = {
                            "date": date,
                            "breakfast": [],
                            "dinner": [],
                            "total_calories_breakfast": None,
                            "total_calories_dinner": None,
                            "isToday": date == today_turkish
                        }
                    
                    # Yemekleri dönüştür
                    meals = [{"name": m, "calories": None} for m in menu]
                    cal_value = self._parse_calorie_range(calories)
                    
                    if meal_type == "breakfast":
                        days_dict[date]["breakfast"] = meals
                        days_dict[date]["total_calories_breakfast"] = cal_value
                    elif meal_type == "dinner":
                        days_dict[date]["dinner"] = meals
                        days_dict[date]["total_calories_dinner"] = cal_value
                
                # Dict'i listeye çevir
                result = list(days_dict.values())
                
                if not result:
                    return self._get_fallback_kyk()
                
                # Cache'e kaydet
                cache.set("kyk_meals", result, self.CACHE_TTL)
                print("KYK: API'den çekildi ve cache'lendi")
                
                return result
                
        except Exception as e:
            print(f"KYK API Hatası: {e}")
            return self._get_fallback_kyk()
    
    def _get_fallback_kyk(self) -> List[Dict]:
        today = datetime.today().strftime("%Y-%m-%d")
        return [{
            "date": self._get_today_turkish(),
            "breakfast": [
                {"name": "Haşlanmış Yumurta", "calories": None},
                {"name": "Beyaz Peynir", "calories": None},
                {"name": "Siyah Zeytin", "calories": None},
                {"name": "Çeyrek Ekmek", "calories": None}
            ],
            "dinner": [
                {"name": "Mercimek Çorbası", "calories": None},
                {"name": "Tavuk Sote", "calories": None},
                {"name": "Bulgur Pilavı", "calories": None},
                {"name": "Cacık", "calories": None}
            ],
            "total_calories_breakfast": 850,
            "total_calories_dinner": 1500,
            "isToday": True
        }]

meal_service = MealService()
