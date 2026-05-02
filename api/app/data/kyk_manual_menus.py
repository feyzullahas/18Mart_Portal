"""
KYK Yemek Menüleri - Manuel Veri
Fotoğraflardan manuel olarak çıkarılmıştır.
Her ay için ayrı bir liste tutulur.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict

def get_tr_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=3)))

def get_manual_kyk_menu(year: int, month: int) -> Optional[List[Dict]]:
    """Manuel KYK menü verisi döndürür. Veri yoksa None döner."""
    key = f"{year}-{month:02d}"
    data = MANUAL_MENUS.get(key)
    if data is None:
        return None
    today = get_tr_now().strftime("%Y-%m-%d")
    return [{**day, "isToday": day["dateRaw"] == today} for day in data]


def _b(names: list) -> list:
    """Kahvaltı öğelerini oluşturur (kalori bilgisi yok)."""
    return [{"name": n, "calories": None} for n in names]


def _d(names: list) -> list:
    """Akşam yemeği öğelerini oluşturur (kalori bilgisi yok)."""
    return [{"name": n, "calories": None} for n in names]


def _day(date_raw: str, date_tr: str, breakfast: list, dinner: list) -> dict:
    return {
        "date": date_tr,
        "dateRaw": date_raw,
        "breakfast": _b(breakfast),
        "dinner": _d(dinner),
        "total_calories_breakfast": None,
        "total_calories_dinner": None,
    }


# ──────────────────────────────────────────────
# MAYIS 2026
# ──────────────────────────────────────────────
_MAY_2026 = [
    _day("2026-05-01", "1 Mayıs 2026 Cuma",
         ["Karışık Kızartma", "Haşlanmış Yumurta", "Kaşar Peynir",
          "Siyah/Yeşil Zeytin", "Reçel Çeşitleri"],
         ["Çeşmi Nigar Çorba / Domates Çorba",
          "Tavuk Külbastı (+Sebze Garnitür) / Karışık Dolma (+Yoğurt)",
          "Makarna (Sos Çeşitleri)", "Karışık Salata"]),

    _day("2026-05-02", "2 Mayıs 2026 Cumartesi",
         ["Kaşarlı Omlet", "Çikolatalı Milföy Börek", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Tarhana Çorba / Düğün Çorba",
          "Kuru Fasulye Yemeği / Karnabahar Kızartma (+Yoğurt)",
          "Şehriyeli Pirinç Pilavı", "Cevizli Baklava"]),

    _day("2026-05-03", "3 Mayıs 2026 Pazar",
         ["Patates Kızartması", "Haşlanmış Yumurta", "Ezine Peynir",
          "Siyah/Yeşil Zeytin", "Tahinli Pekmez"],
         ["Ezogelin Çorba / Sebze Çorba",
          "Beşamel Soslu Tavuk / Taze Fasulye",
          "Arpa Şehriye Pilavı", "Haydari"]),

    _day("2026-05-04", "4 Mayıs 2026 Pazartesi",
         ["Peynirli Omlet", "Dere Otlu Poğaça", "Krem Peynir",
          "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Yayla Çorba / Salçalı Şehriye Çorba",
          "Et Fajita (+Lavaş) / Soslu Karışık Kızartma",
          "Bulgur Pilavı", "Ayran"]),

    _day("2026-05-05", "5 Mayıs 2026 Salı",
         ["Sosis Kokteyl (Kızartma)", "Haşlanmış Yumurta", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Bal+Tereyağ"],
         ["Mercimek Çorba / Toyga Çorba",
          "Garnitürlü Tavuk Sote / Barbunya Yemeği",
          "Pirinç Pilavı", "Kuru Cacık"]),

    _day("2026-05-06", "6 Mayıs 2026 Çarşamba",
         ["Menemen", "Zeytinli/Peynirli Açma", "Kaşar Peynir",
          "Siyah/Yeşil Zeytin", "Elma"],
         ["Yüksük Çorba / Tarhana Çorba",
          "Izgara Köfte (+Elma Dilim Patates) / Mücver (+Yoğurt)",
          "Salçalı Bulgur Pilavı", "Çikolata Soslu Sütlü İrmik Tatlısı"]),

    _day("2026-05-07", "7 Mayıs 2026 Perşembe",
         ["Patates Kızartması", "Haşlanmış Yumurta", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Tahinli Pekmez"],
         ["Çeşmi Nigar Çorba / Domates Çorba",
          "Köri Soslu Tavuk / Biber Dolma (+Yoğurt)",
          "Spagetti Napoliten", "Çoban Salata"]),

    _day("2026-05-08", "8 Mayıs 2026 Cuma",
         ["Sucuklu Yumurta", "Simit", "Kaşar Peynir",
          "Siyah/Yeşil Zeytin", "Bal+Tereyağ"],
         ["Düğün Çorba / Şafak Çorba",
          "Nohut Yemeği / Ratatuy",
          "Şehriyeli Pirinç Pilavı", "Cacık"]),

    _day("2026-05-09", "9 Mayıs 2026 Cumartesi",
         ["Karışık Pizza", "Haşlanmış Yumurta", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Sürülebilir Çikolata"],
         ["Ezogelin Çorba / Köz Biber Çorba",
          "Izgara Tavuk (+Sebze Garnitür) / Bezelye Yemeği",
          "Yoğurtlu Mantı Makarna", "Tahinli Cevizli Kemalpaşa Tatlısı"]),

    _day("2026-05-10", "10 Mayıs 2026 Pazar",
         ["Kaşarlı Omlet", "Sade Poğaça", "Tulum Peynir",
          "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Salçalı Şehriye Çorba / Havuç Çorba",
          "Hünkar Beğendi / Sebze Graten",
          "Pirinç Pilavı", "Karışık Salata"]),

    _day("2026-05-11", "11 Mayıs 2026 Pazartesi",
         ["Patates Kavurması", "Haşlanmış Yumurta", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Reçel Çeşitleri"],
         ["Tavuk Çorba / Domates Çorba",
          "Mengen Musakka / Falafel (+Yoğurt)",
          "Bulgur Pilavı", "Tiramisu"]),

    _day("2026-05-12", "12 Mayıs 2026 Salı",
         ["Sade Omlet", "Zeytinli/Peynirli Açma", "Labne Peynir",
          "Siyah/Yeşil Zeytin", "Bal+Tereyağ"],
         ["Mercimek Çorba / Yayla Çorba",
          "Lavaşta Tavuk Tantuni / Taze Fasulye",
          "Salçalı Makarna", "Ayran"]),

    _day("2026-05-13", "13 Mayıs 2026 Çarşamba",
         ["Patates Kızartması", "Haşlanmış Yumurta", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Tarhana Çorba / Kremalı Mantar Çorba",
          "Çoban Kavurma / Yoğurtlu Karnabahar Kızartma",
          "Havuçlu Pirinç Pilavı", "Çiğköfte"]),

    _day("2026-05-14", "14 Mayıs 2026 Perşembe",
         ["Peynirli Omlet", "Çikolatalı Milföy Börek", "Kaşar Peynir",
          "Siyah/Yeşil Zeytin", "Tahinli Pekmez"],
         ["Çeşmi Nigar Çorba / Sebze Çorba",
          "Galeta Unlu Tavuk (+Garnitür) / Mercimek Yemeği",
          "Sebzeli Bulgur Pilavı", "Kadayıflı Muhallebi"]),

    _day("2026-05-15", "15 Mayıs 2026 Cuma",
         ["Patates Salatası", "Haşlanmış Yumurta", "Çeçil Peynir",
          "Siyah/Yeşil Zeytin", "Helva"],
         ["Anadolu Çorba / Salçalı Şehriye Çorba",
          "Hamburger / Kabak Sandal",
          "Fırın Makarna", "Ayran"]),

    _day("2026-05-16", "16 Mayıs 2026 Cumartesi",
         ["Menemen", "Simit", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Sürülebilir Çikolata"],
         ["Ezogelin Çorba / Köz Biber Çorba",
          "Tavuk Külbastı (+Garnitür) / Mantar Sote",
          "Pirinç Pilavı", "Armut"]),

    _day("2026-05-17", "17 Mayıs 2026 Pazar",
         ["Sosisli Patates Kızartması", "Haşlanmış Yumurta", "Kaşar Peynir",
          "Siyah/Yeşil Zeytin", "Bal+Tereyağ"],
         ["Düğün Çorba / Domates Çorba",
          "Nohut Yemeği / Yoğurtlu Yaz Kızartma",
          "Bulgur Pilavı", "Kremşantili Haşhaşlı Revani"]),

    _day("2026-05-18", "18 Mayıs 2026 Pazartesi",
         ["Kaşarlı Omlet", "Dere Otlu Poğaça", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Tahinli Pekmez"],
         ["Mercimek Çorba / Kremalı Mantar Çorba",
          "Tavuk Sote (Susamlı) / Taze Fasulye",
          "Pirinç Pilavı", "Rus Salatası"]),

    _day("2026-05-19", "19 Mayıs 2026 Salı",
         ["Patates Kızartması", "Haşlanmış Yumurta", "Krem Peynir",
          "Siyah/Yeşil Zeytin", "Muz"],
         ["Terbiyeli Şehriye Çorba / Tarhana Çorba",
          "Tas Kebabı / Yoğurtlu Karnabahar Kızartma",
          "Spagetti Napoliten", "Kremalı Çikolatalı Pasta"]),

    _day("2026-05-20", "20 Mayıs 2026 Çarşamba",
         ["Sucuklu Yumurta", "Zeytinli/Peynirli Açma", "Kaşar Peynir",
          "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Çeşmi Nigar Çorba / Yayla Çorba",
          "Izgara Tavuk (+Sebze Garnitür) / Yeşil Mercimek Yemeği",
          "Sebzeli Bulgur Pilavı", "Ege Salata"]),

    _day("2026-05-21", "21 Mayıs 2026 Perşembe",
         ["Patates Kavurması", "Haşlanmış Yumurta", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Reçel Çeşitleri"],
         ["Salçalı Şehriye Çorba / Havuç Çorba",
          "Yarım Ekmek Arası Köfte / Biber Dolma",
          "Makarna (Sos Çeşitleri)", "Ayran"]),

    _day("2026-05-22", "22 Mayıs 2026 Cuma",
         ["Menemen", "Kalem Böreği", "Kaşar Peynir",
          "Siyah/Yeşil Zeytin", "Sürülebilir Çikolata"],
         ["Tavuk Çorba / Şafak Çorba",
          "Kuru Fasulye Yemeği / Soslu Karışık Kızartma",
          "Şehriyeli Pirinç Pilavı", "Tulumba Tatlısı / Cacık"]),

    _day("2026-05-23", "23 Mayıs 2026 Cumartesi",
         ["Sosis Kokteyl (Salçalı)", "Haşlanmış Yumurta", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Bal+Tereyağ"],
         ["Ezogelin Çorba / Düğün Çorba",
          "Tavuk Şiş / İmam Bayıldı",
          "Salçalı Makarna", "Yoğurt"]),

    _day("2026-05-24", "24 Mayıs 2026 Pazar",
         ["Peynirli Omlet", "Sade Poğaça", "Ezine Peynir",
          "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Domates Çorba / Toyga Çorba",
          "Çökertme Kebabı / Bezelye Yemeği",
          "Bulgur Pilavı", "Sütlaç"]),

    _day("2026-05-25", "25 Mayıs 2026 Pazartesi",
         ["Patates Kızartması", "Haşlanmış Yumurta", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Reçel Çeşitleri"],
         ["Mercimek Çorba / Sebze Çorba",
          "Hamburger / Barbunya Yemeği",
          "Spagetti Napoliten", "Ayran"]),

    _day("2026-05-26", "26 Mayıs 2026 Salı",
         ["Menemen", "Simit", "Kaşar Peynir",
          "Siyah/Yeşil Zeytin", "Sürülebilir Çikolata"],
         ["Mahluta Çorba / Yayla Çorba",
          "Galeta Unlu Tavuk (+Garnitür) / Türlü Yemeği",
          "Domatesli Bulgur Pilavı", "Çoban Salata"]),

    _day("2026-05-27", "27 Mayıs 2026 Çarşamba",
         ["Karışık Pizza", "Haşlanmış Yumurta", "Labne Peynir",
          "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Çeşmi Nigar Çorba / Havuç Çorba",
          "Et Kavurma (+Elma Dilim Patates) / Biber Dolma (+Yoğurt)",
          "Arpa Şehriye Pilavı", "Cevizli Baklava"]),

    _day("2026-05-28", "28 Mayıs 2026 Perşembe",
         ["Kaşarlı Omlet", "Patates Kroket", "Örgü Peynir",
          "Siyah/Yeşil Zeytin", "Helva"],
         ["Salçalı Şehriye Çorba / Kremalı Mantar Çorba",
          "Lavaşta Tavuk Tantuni / Taze Fasulye",
          "Garnitürlü Pirinç Pilavı", "Ayran"]),

    _day("2026-05-29", "29 Mayıs 2026 Cuma",
         ["Sosisli Patates Kızartması", "Haşlanmış Yumurta", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Bal+Tereyağ"],
         ["Ezogelin Çorba / Şafak Çorba",
          "Çiftlik Köfte / Mücver (+Yoğurt)",
          "Cevizli Erişte", "Fıstıklı İrmik Helvası"]),

    _day("2026-05-30", "30 Mayıs 2026 Cumartesi",
         ["Sade Omlet", "Zeytinli/Peynirli Açma", "Kaşar Peynir",
          "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Tarhana Çorba / Köz Biber Çorba",
          "Nohut Yemeği / Yoğurtlu Yaz Kızartma",
          "Şehriyeli Pirinç Pilavı", "Muz"]),

    _day("2026-05-31", "31 Mayıs 2026 Pazar",
         ["Patates Salatası", "Haşlanmış Yumurta", "Beyaz Peynir",
          "Siyah/Yeşil Zeytin", "Tahinli Pekmez"],
         ["Düğün Çorba / Domates Çorba",
          "Karnıyarık / Yoğurtlu Karnabahar Kızartma",
          "Salçalı Bulgur Pilavı", "Triliçe"]),
]

MANUAL_MENUS = {
    "2026-05": _MAY_2026,
}
