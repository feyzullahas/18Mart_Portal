from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import calendar

from app.data.kyk_manual_menus import get_manual_kyk_menu


def get_tr_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=3)))


class MealService:
    def _format_tr_date(self, dt: datetime) -> str:
        months = {
            1: "Ocak",
            2: "Şubat",
            3: "Mart",
            4: "Nisan",
            5: "Mayıs",
            6: "Haziran",
            7: "Temmuz",
            8: "Ağustos",
            9: "Eylül",
            10: "Ekim",
            11: "Kasım",
            12: "Aralık",
        }
        days = {
            0: "Pazartesi",
            1: "Salı",
            2: "Çarşamba",
            3: "Perşembe",
            4: "Cuma",
            5: "Cumartesi",
            6: "Pazar",
        }
        return f"{dt.day} {months[dt.month]} {dt.year} {days[dt.weekday()]}"

    def _meal(self, name: str, calories: Optional[int]) -> Dict:
        return {"name": name, "calories": calories}

    def _closed_menu(self) -> List[Dict]:
        return [{"name": "ÖSEM kapalı", "calories": None}]

    def _osem_menus_may_2026(self) -> Dict[str, List[tuple]]:
        return {
            "2026-05-04": [
                ("Tavuksuyu Çorba", 135),
                ("Et Haşlama", 381),
                ("Sade Bulgur Pilavı", 271),
                ("Kemalpaşa Tatlısı", 301),
            ],
            "2026-05-05": [
                ("Ezogelin Çorba", 203),
                ("Tavuk Sote", 336),
                ("Yoğurtlu Mantı", 436),
                ("Mısırlı Kıvırcık Salata", 94),
            ],
            "2026-05-06": [
                ("Mercimek Çorba", 216),
                ("Hünkarbeğendi", 545),
                ("Şehriyeli Kuskus", 353),
                ("Cacık", 116),
            ],
            "2026-05-07": [
                ("Domates Çorba", 109),
                ("Tavuk Döner", 193),
                ("Elma Dilim Patates", 170),
                ("Arpa Şeh. Pirinç Pilavı", 345),
                ("Ayran", 74),
            ],
            "2026-05-08": [
                ("Buğday Çorba", 131),
                ("İzmir Köfte", 442),
                ("Makarna Kavurma", 310),
                ("Muhallebi", 381),
            ],
            "2026-05-11": [
                ("Tarhana Çorba", 118),
                ("Kıy. Çökertme Kebabı", 420),
                ("Tel Şeh. Pirinç Pilavı", 345),
                ("Tulumba Tatlısı", 414),
            ],
            "2026-05-12": [
                ("Sebze Çorba", 178),
                ("Soslu Tavuk But", 382),
                ("Kızarmış Biber", 6),
                ("Peynirli Erişte", 293),
                ("Kakaolu Puding", 296),
            ],
            "2026-05-13": [
                ("Ezogelin Çorba", 203),
                ("Et Döner", 280),
                ("Karışık Salata", 41),
                ("Arpa Şehriye Pilavı", 360),
                ("Ayran", 74),
            ],
            "2026-05-14": [
                ("Mercimek Çorba", 216),
                ("Tavuk Şinitzel", 404),
                ("Patates Salatası", 122),
                ("Fırın Makarna", 431),
                ("Meyve", 100),
            ],
            "2026-05-15": [
                ("Toyga Çorba", 167),
                ("Çoban Kavurma", 293),
                ("Lavaş", 170),
                ("Biberli Bulgur Pilavı", 280),
                ("Yoğurt", 93),
            ],
            "2026-05-18": [
                ("Ezogelin Çorba", 203),
                ("Fırın Köfte", 444),
                ("Fasulye Piyazı", 93),
                ("Kısır", 288),
                ("Karışık Turşu", 21),
            ],
            "2026-05-20": [
                ("Buğday Çorba", 131),
                ("Patlıcan Musakka", 439),
                ("Bahar Pilavı", 282),
                ("Kadayıf", 405),
            ],
            "2026-05-21": [
                ("Arpa Şehriye Çorba", 125),
                ("Patatesli Çıtır Tavuk", 394),
                ("Sosyete Mantısı", 413),
                ("Meyve Suyu", 100),
            ],
            "2026-05-22": [
                ("Mercimek Çorba", 216),
                ("Tas Kebabı", 402),
                ("Patates Püresi", 127),
                ("Mısırlı Kuskus", 323),
                ("Fıstıklı İrmik Helvası", 370),
            ],
            "2026-05-25": [
                ("Domates Çorba", 109),
                ("Et Sote", 280),
                ("Lavaş", 170),
                ("Nohutlu Pirinç Pilavı", 342),
                ("Ayran", 74),
            ],
            "2026-05-26": [
                ("Mercimek Çorba", 216),
                ("Köri Soslu Tavuk", 250),
                ("Dom. Sos. Spagetti", 316),
                ("Keşkül", 322),
            ],
        }

    def _osem_menus_june_2026(self) -> Dict[str, List[tuple]]:
        return {
            "2026-06-01": [("Tavuksuyu Çorba", 135), ("Patlıcan Musakka", 439), ("Nohutlu Bulgur Pilavı", 302), ("Yoğurt", 93)],
            "2026-06-02": [("Buğday Çorba", 131), ("Fırın Tavuk But", 383), ("Kızarmış Biber", 6), ("Tel Şehriyeli Pirinç Pilavı", 345), ("Kazandibi", 387)],
            "2026-06-03": [("Ezogelin Çorba", 203), ("Macar Gulaş", 323), ("Patates Püresi", 127), ("Arpa Şehriye Pilavı", 360), ("Cevizli Baklava", 487)],
            "2026-06-04": [("Mercimek Çorba", 216), ("Barbekü Soslu Tavuk", 226), ("Yoğurtlu Mantı", 434), ("Karpuz", 140)],
            "2026-06-05": [("Domates Çorba", 109), ("Et Burger", 274), ("Elma Dilim Patates", 170), ("Peynirli Makarna", 370), ("Ayran", 74)],
            "2026-06-08": [("Ezogelin Çorba", 203), ("Ekşili Köfte", 467), ("Erişte Kavurma", 235), ("Kemalpaşa Tatlısı", 301)],
            "2026-06-09": [("Düğün Çorba", 124), ("Tavuk Pane", 353), ("Rus Salatası", 172), ("Kısır", 288), ("Meyve Suyu", 100)],
            "2026-06-10": [("Tarhana Çorba", 118), ("Hünkarbeğendi", 545), ("Yeşil Mercimekli Bulgur Pilavı", 310), ("Fıstıklı İrmik Helvası", 370)],
            "2026-06-11": [("Sebze Çorba", 128), ("Tavuk Döner", 193), ("Domates Salatası", 44), ("Dereotlu Pirinç Pilavı", 311), ("Ayran", 74)],
            "2026-06-12": [("Mercimek Çorba", 216), ("Ankara Tava", 549), ("Su Böreği", 419), ("Yoğurtlu Semizotu Salatası", 170)],
            "2026-06-15": [("Domates Çorba", 109), ("Buğu Kebabı", 436), ("Şehriyeli Kuskus", 353), ("Çikolatalı Puding", 451)],
            "2026-06-16": [("Ezogelin Çorba", 203), ("Kadınbudu Köfte", 553), ("Haydari", 55), ("Fırın Makarna", 431), ("Nektarin", 65)],
            "2026-06-17": [("Buğday Çorba", 131), ("Kıymalı Ali Nazik", 420), ("Nohutlu Pirinç Pilavı", 342), ("Aşure", 513)],
            "2026-06-18": [("Mercimek Çorba", 216), ("Beşamel Soslu Tavuk", 459), ("Domates Soslu Spagetti", 316), ("Mısırlı Kıvırcık Salata", 94)],
            "2026-06-19": [("Tavuksuyu Çorba", 135), ("Soslu Fırın Köfte", 444), ("Fasulye Piyazı", 93), ("Arpa Şehriye Pilavı", 360), ("Yoğurt", 93)],
            "2026-06-22": [("Toyga Çorba", 167), ("Et Döner", 280), ("Lavaş", 170), ("Melek Pilavı", 350), ("Ayran", 74)],
            "2026-06-23": [("Tarhana Çorba", 118), ("Tavuk Kanat", 382), ("Çoban Salata", 32), ("Sade Bulgur Pilavı", 271), ("Keşkül", 322)],
            "2026-06-24": [("Ezogelin Çorba", 203), ("Beğendili Misket Köfte", 488), ("Erişte Kavurma", 235), ("Cacık", 116)],
            "2026-06-25": [("Düğün Çorba", 124), ("Tavuk Sote", 336), ("Zeytinyağlı Biber Dolma", 303), ("Yoğurt", 93)],
            "2026-06-26": [("Arpa Şehriye Çorba", 118), ("Karnıyarık", 451), ("Bahar Pilavı", 282), ("Kadayıf", 405)],
        }

    def _build_osem_month(self, year: int, month: int) -> List[Dict]:
        menus = {}
        if year == 2026 and month == 5:
            menus = self._osem_menus_may_2026()
        elif year == 2026 and month == 6:
            menus = self._osem_menus_june_2026()
        
        days_in_month = calendar.monthrange(year, month)[1]
        result: List[Dict] = []
        for day in range(1, days_in_month + 1):
            date_raw = f"{year}-{month:02d}-{day:02d}"
            dt = datetime(year, month, day)
            date_tr = self._format_tr_date(dt)
            items = menus.get(date_raw)
            if items:
                menu = [self._meal(name, cal) for name, cal in items]
                total_calories = sum(cal for _, cal in items if cal is not None)
            else:
                menu = self._closed_menu()
                total_calories = None
            result.append(
                {
                    "date": date_tr,
                    "dateRaw": date_raw,
                    "menu": menu,
                    "total_calories": total_calories,
                }
            )
        return result

    async def get_osem_meals(self) -> List[Dict]:
        now = get_tr_now()
        data = self._build_osem_month(now.year, now.month)
        today = now.strftime("%Y-%m-%d")
        return [{**day, "isToday": day["dateRaw"] == today} for day in data]

    async def get_kyk_meals(self, year: Optional[int] = None, month: Optional[int] = None) -> List[Dict]:
        now = get_tr_now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        manual = get_manual_kyk_menu(year, month)
        if manual is not None:
            return manual
        return self._get_fallback_kyk()

    def _get_fallback_kyk(self) -> List[Dict]:
        today = get_tr_now().strftime("%Y-%m-%d")
        return [
            {
                "date": self._format_tr_date(get_tr_now()),
                "dateRaw": today,
                "breakfast": [
                    {"name": "Haşlanmış Yumurta", "calories": None},
                    {"name": "Beyaz Peynir", "calories": None},
                    {"name": "Siyah Zeytin", "calories": None},
                    {"name": "Çeyrek Ekmek", "calories": None},
                ],
                "dinner": [
                    {"name": "Mercimek Çorbası", "calories": None},
                    {"name": "Tavuk Sote", "calories": None},
                    {"name": "Bulgur Pilavı", "calories": None},
                    {"name": "Cacık", "calories": None},
                ],
                "total_calories_breakfast": 850,
                "total_calories_dinner": 1500,
                "isToday": True,
            }
        ]


meal_service = MealService()
