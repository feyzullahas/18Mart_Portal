import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta, timezone
import re

def get_tr_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=3)))

import json
from app.data.kyk_manual_menus import get_manual_kyk_menu

# Basit memory cache
class SimpleCache:
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
    
    def get(self, key: str) -> Optional[any]:
        if key in self._cache:
            item = self._cache[key]
            if get_tr_now() < item["expires"]:
                return item["data"]
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, data: any, ttl_minutes: int = 60):
        self._cache[key] = {
            "data": data,
            "expires": get_tr_now() + timedelta(minutes=ttl_minutes)
        }

def _minutes_until_midnight() -> int:
    """Gece yarısına kadar kalan dakika sayısını döndürür (minimum 1 dakika)"""
    now = get_tr_now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(1, int((midnight - now).total_seconds() / 60))

cache = SimpleCache()

class MealService:
    OSEM_URL = "https://yemek.comu.edu.tr/"
    KYK_BASE_URL = "https://kykyemekliste.com"
    KYK_CITY = "Çanakkale"

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
        now = get_tr_now()
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

    def _normalize_city_name(self, name: str) -> str:
        return (
            name.lower()
            .replace("ç", "c")
            .replace("ğ", "g")
            .replace("ı", "i")
            .replace("ö", "o")
            .replace("ş", "s")
            .replace("ü", "u")
            .replace(" ", "")
            .replace("-", "")
        )

    def _parse_kyk_item_list(self, names: str, calories: Optional[str]) -> List[Dict]:
        if not names:
            return []
        name_parts = [part.strip() for part in re.split(r"\s*/\s*", names) if part.strip()]
        cal_parts = [part.strip() for part in (calories or "").split(",") if part.strip()]

        items = []
        for idx, name in enumerate(name_parts):
            cal_val = None
            if idx < len(cal_parts):
                range_val = self._parse_calorie_range(cal_parts[idx])
                if range_val is not None:
                    cal_val = range_val
                else:
                    digits = re.findall(r"\d+", cal_parts[idx])
                    cal_val = int(digits[0]) if digits else None
            items.append({"name": name, "calories": cal_val})
        return items

    def _parse_total_calories(self, value: Optional[Any]) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return int(value)
        digits = re.findall(r"\d+", str(value))
        return int(digits[0]) if digits else None

    async def get_osem_meals(self) -> List[Dict]:
        """ÖSEM web sitesinden tüm günlerin yemek listesini çeker (günlük cache)"""
        today_str = get_tr_now().strftime("%Y-%m-%d")
        cache_key = f"osem_meals_{today_str}"
        cached = cache.get(cache_key)
        if cached:
            print("ÖSEM: Cache'den döndü")
            return cached

        print("ÖSEM: Yeni veri çekiliyor...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.OSEM_URL, timeout=10.0)
                
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
                
                today = get_tr_now().strftime("%Y-%m-%d")
                
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

                cache.set(cache_key, all_days, _minutes_until_midnight())
                return all_days
                
        except Exception as e:
            print(f"ÖSEM Scraping Hatası: {e}")
            return self._get_fallback_osem()
    
    def _get_fallback_osem(self) -> List[Dict]:
        today = get_tr_now().strftime("%Y-%m-%d")
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

    async def _fetch_kyk_city_id(self, client: httpx.AsyncClient) -> int:
        cache_key = f"kyk_city_id_{self.KYK_CITY}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        response = await client.get(f"{self.KYK_BASE_URL}/api/city", timeout=10.0)
        response.raise_for_status()
        cities = response.json()
        target = self._normalize_city_name(self.KYK_CITY)
        for city in cities:
            name = city.get("name", "")
            if self._normalize_city_name(name) == target:
                cache.set(cache_key, city.get("id"), _minutes_until_midnight())
                return city.get("id")

        raise Exception(f"KYK şehir bulunamadı: {self.KYK_CITY}")

    async def _fetch_kyk_menu_list(self, client: httpx.AsyncClient, city_id: int, meal_type: int) -> List[Dict]:
        url = f"{self.KYK_BASE_URL}/api/menu/liste?cityId={city_id}&mealType={meal_type}"
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []

    async def get_kyk_meals(self, year: Optional[int] = None, month: Optional[int] = None) -> List[Dict]:
        """KYK yemek listesini getirir. Önce manuel veriyi kontrol eder, yoksa API'den çeker."""
        now = get_tr_now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month

        # 1) Önce manuel veriyi kontrol et
        manual = get_manual_kyk_menu(year, month)
        if manual is not None:
            print(f"KYK: Manuel veriden döndü ({year}-{month:02d}, {len(manual)} gün)")
            return manual

        # 2) Cache key'i ay ve yıla göre oluştur
        cache_key = f"kyk_meals_{year}_{month}"
        cached = cache.get(cache_key)
        if cached:
            print(f"KYK: Cache'den döndü ({year}-{month})")
            return cached

        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                follow_redirects=True,
                timeout=10.0
            ) as client:
                city_id = await self._fetch_kyk_city_id(client)

                breakfast_list, dinner_list = await asyncio.gather(
                    self._fetch_kyk_menu_list(client, city_id, 0),
                    self._fetch_kyk_menu_list(client, city_id, 1)
                )

                def in_requested_month(date_str: str) -> bool:
                    try:
                        dt = datetime.strptime(date_str, "%Y-%m-%d")
                        return dt.year == year and dt.month == month
                    except ValueError:
                        return False

                today = now.date()
                combined: Dict[str, Dict] = {}

                for item in breakfast_list:
                    date_raw = item.get("date", "")
                    if not in_requested_month(date_raw):
                        continue
                    entry = combined.setdefault(date_raw, {
                        "date": self._format_date(date_raw),
                        "dateRaw": date_raw,
                        "breakfast": [],
                        "dinner": [],
                        "total_calories_breakfast": None,
                        "total_calories_dinner": None,
                        "isToday": date_raw == today.strftime("%Y-%m-%d"),
                    })
                    meals = []
                    meals += self._parse_kyk_item_list(item.get("first", ""), item.get("firstCalories"))
                    meals += self._parse_kyk_item_list(item.get("second", ""), item.get("secondCalories"))
                    meals += self._parse_kyk_item_list(item.get("third", ""), item.get("thirdCalories"))
                    meals += self._parse_kyk_item_list(item.get("fourth", ""), item.get("fourthCalories"))
                    entry["breakfast"] = meals
                    entry["total_calories_breakfast"] = self._parse_total_calories(item.get("totalCalories"))

                for item in dinner_list:
                    date_raw = item.get("date", "")
                    if not in_requested_month(date_raw):
                        continue
                    entry = combined.setdefault(date_raw, {
                        "date": self._format_date(date_raw),
                        "dateRaw": date_raw,
                        "breakfast": [],
                        "dinner": [],
                        "total_calories_breakfast": None,
                        "total_calories_dinner": None,
                        "isToday": date_raw == today.strftime("%Y-%m-%d"),
                    })
                    meals = []
                    meals += self._parse_kyk_item_list(item.get("first", ""), item.get("firstCalories"))
                    meals += self._parse_kyk_item_list(item.get("second", ""), item.get("secondCalories"))
                    meals += self._parse_kyk_item_list(item.get("third", ""), item.get("thirdCalories"))
                    meals += self._parse_kyk_item_list(item.get("fourth", ""), item.get("fourthCalories"))
                    entry["dinner"] = meals
                    entry["total_calories_dinner"] = self._parse_total_calories(item.get("totalCalories"))

                result = sorted(combined.values(), key=lambda x: x.get("dateRaw", ""))

                if not result:
                    return self._get_fallback_kyk()

                cache.set(cache_key, result, _minutes_until_midnight())
                print(f"KYK: kykyemekliste.com'dan çekildi ve cache'lendi ({year}-{month}, {len(result)} gün)")
                return result

        except Exception as e:
            print(f"KYK Scraping Hatası: {e}")
            return self._get_fallback_kyk()
    
    def _get_fallback_kyk(self) -> List[Dict]:
        today = get_tr_now().strftime("%Y-%m-%d")
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
