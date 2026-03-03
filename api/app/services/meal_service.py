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
    KYK_BASE_URL = "https://kykyemek.com"
    KYK_CITY = "Çanakkale"
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

    def _parse_turkish_date(self, date_str: str) -> Optional[datetime]:
        """'1 Mart 2026 Pazar' formatındaki Türkçe tarihi datetime objesine çevirir"""
        months_tr = {
            'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4,
            'mayıs': 5, 'haziran': 6, 'temmuz': 7, 'ağustos': 8,
            'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12
        }
        try:
            parts = date_str.strip().split()
            if len(parts) < 3:
                return None
            day = int(parts[0])
            month = months_tr.get(parts[1].lower())
            year = int(parts[2])
            if month is None:
                return None
            return datetime(year, month, day)
        except (ValueError, IndexError):
            return None

    def _parse_kyk_cards(self, html: str) -> List[Dict]:
        """kykyemek.com AJAX yanıtındaki HTML kartlarını parse eder"""
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("div", class_="card")
        result = []
        for card in cards:
            date_p = card.find("p", class_="date")
            if not date_p:
                continue
            date_text = date_p.get_text(strip=True)

            body = card.find("div", class_="card-body")
            foods = []
            calories_text = None
            if body:
                for p in body.find_all("p"):
                    t = p.get_text(strip=True)
                    if not t:
                        continue
                    if "kalori" in t.lower():
                        calories_text = t
                    else:
                        foods.append(t)

            cal_value = self._parse_calorie_range(calories_text) if calories_text else None
            meals = [{"name": f, "calories": None} for f in foods]
            result.append({
                "date_text": date_text,
                "meals": meals,
                "total_calories": cal_value,
            })
        return result

    async def _fetch_kyk_html(self, client: httpx.AsyncClient, meal_type_dinner: bool, month_shift: int) -> str:
        """kykyemek.com AJAX endpoint'inden HTML çeker (session cookie gerektirir)"""
        params = {
            "city": self.KYK_CITY,
            "mealType": str(meal_type_dinner).lower(),
            "hidePast": "false",
            "monthShift": month_shift,
        }
        ajax_headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.KYK_BASE_URL}/",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }
        url = f"{self.KYK_BASE_URL}/Menu/GetDailyMenu/{self.KYK_CITY}"
        response = await client.get(url, params=params, headers=ajax_headers, timeout=15.0)
        if response.status_code != 200:
            raise Exception(f"KYK AJAX isteği başarısız: {response.status_code}")
        data = response.json()
        return data.get("html", "")

    async def get_kyk_meals(self, year: Optional[int] = None, month: Optional[int] = None) -> List[Dict]:
        """kykyemek.com'dan tüm günlerin yemek listesini çeker (kahvaltı + akşam)"""
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month

        # monthShift hesapla (kykyemek.com mevcut aya göre ofset kullanıyor)
        month_shift = (year - now.year) * 12 + (month - now.month)

        # monthShift sınır kontrolü (-2 ile +2 arası destekleniyor)
        if month_shift < -2 or month_shift > 2:
            print(f"KYK: monthShift={month_shift} desteklenmiyor (max ±2). Fallback dönülüyor.")
            return self._get_fallback_kyk()

        # Cache key'i ay ve yıla göre oluştur
        cache_key = f"kyk_meals_{year}_{month}"
        cached = cache.get(cache_key)
        if cached:
            print(f"KYK: Cache'den döndü ({year}-{month})")
            return cached

        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                follow_redirects=True,
                timeout=20.0
            ) as client:
                # Önce ana sayfayı ziyaret ederek session cookie'lerini al
                await client.get(f"{self.KYK_BASE_URL}/", timeout=15.0)

                # Kahvaltı ve akşam yemeği verilerini paralel çek
                breakfast_html = await self._fetch_kyk_html(client, False, month_shift)
                dinner_html = await self._fetch_kyk_html(client, True, month_shift)

                breakfast_cards = self._parse_kyk_cards(breakfast_html)
                dinner_cards = self._parse_kyk_cards(dinner_html)

                # Akşam yemeğini tarih bazlı dict'e çevir
                dinner_by_date = {}
                for card in dinner_cards:
                    dinner_by_date[card["date_text"]] = card

                today = now.date()
                result = []
                for b_card in breakfast_cards:
                    date_text = b_card["date_text"]
                    dt = self._parse_turkish_date(date_text)
                    is_today = (dt.date() == today) if dt else False

                    d_card = dinner_by_date.get(date_text, {})

                    result.append({
                        "date": date_text,
                        "dateRaw": dt.strftime("%Y-%m-%d") if dt else "",
                        "breakfast": b_card.get("meals", []),
                        "dinner": d_card.get("meals", []),
                        "total_calories_breakfast": b_card.get("total_calories"),
                        "total_calories_dinner": d_card.get("total_calories"),
                        "isToday": is_today,
                    })

                if not result:
                    return self._get_fallback_kyk()

                cache.set(cache_key, result, self.CACHE_TTL)
                print(f"KYK: kykyemek.com'dan çekildi ve cache'lendi ({year}-{month}, {len(result)} gün)")
                return result

        except Exception as e:
            print(f"KYK Scraping Hatası: {e}")
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
