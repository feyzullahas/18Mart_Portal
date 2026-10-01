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


def _day(date_raw: str, date_tr: str, breakfast: list, dinner: list, total_calories_breakfast: int = None, total_calories_dinner: int = None) -> dict:
    return {
        "date": date_tr,
        "dateRaw": date_raw,
        "breakfast": _b(breakfast),
        "dinner": _d(dinner),
        "total_calories_breakfast": total_calories_breakfast,
        "total_calories_dinner": total_calories_dinner,
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
         ["Sosili Patates Kızartması", "Haşlanmış Yumurta", "Beyaz Peynir",
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

# ──────────────────────────────────────────────
# HAZİRAN 2026
# ──────────────────────────────────────────────
_JUNE_2026 = [
    _day("2026-06-01", "1 Haziran 2026 Pazartesi",
         ["Sucuklu Yumurta", "Dere Otlu Poğaça", "Ezine Peynir", "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Mercimek Çorbası / Yayla Çorbası", "Garnitürlü Tavuk Sarma / Bezelye Yemeği", "Salçalı Makarna", "Cacık"]),
    _day("2026-06-02", "2 Haziran 2026 Salı",
         ["Patates Kızartması", "Haşlanmış Yumurta", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Elma"],
         ["Terbiyeli Şehriye Çorbası / Tarhana Çorbası", "Pideli Köfte / Galeta Unlu Tavuk+Garnitür / Taze Fasulye", "Şehriyeli Pirinç Pilavı", "Çoban Salata"]),
    _day("2026-06-03", "3 Haziran 2026 Çarşamba",
         ["Peynirli Omlet", "Çikolatalı Milföy Börek", "Kaşar Peynir", "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Ezogelin Çorbası / Sebze Çorbası", "Çökertme Kebabı / Izgara Tavuk+Garnitür / Yoğurtlu Yaz Kızartma", "Domatesli Bulgur Pilavı", "Tiramisu"]),
    _day("2026-06-04", "4 Haziran 2026 Perşembe",
         ["Karışık Pizza", "Haşlanmış Yumurta", "Krem Peynir", "Siyah/Yeşil Zeytin", "Reçel Çeşitleri"],
         ["Salçalı Şehriye Çorbası / Anadolu Çorbası", "Lavaşta Tavuk Tantuni / Kabak Sandal", "Spagetti Napoliten", "Ayran"]),
    _day("2026-06-05", "5 Haziran 2026 Cuma",
         ["Menemen", "Sade Poğaça", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Tahinli Pekmez"],
         ["Düğün Çorbası / Çeşmi Nigar Çorbası", "Kuru Fasulye Yemeği / İmam Bayıldı", "Pirinç Pilavı", "Karışık Salata"]),
    _day("2026-06-06", "6 Haziran 2026 Cumartesi",
         ["Karışık Kızartma", "Haşlanmış Yumurta", "Kaşar Peynir", "Siyah/Yeşil Zeytin", "Sürülebilir Çikolata"],
         ["Domates Çorbası / Toyga Çorbası", "Çoban Kavurma / Tavuk Sote / Falafel+Yoğurt", "Sebzeli Bulgur Pilavı", "Ezme"]),
    _day("2026-06-07", "7 Haziran 2026 Pazar",
         ["Sade Omlet", "Peynirli/Ispanaklı Börek", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Mercimek Çorbası / Havuç Çorbası", "Tavuk Şiş+Garnitür / Yeşil Mercimek Yemeği", "Şehriyeli Pirinç Pilavı", "Kalburabastı"]),
    _day("2026-06-08", "8 Haziran 2026 Pazartesi",
         ["Patates Kavurması", "Haşlanmış Yumurta", "Kaşar Peynir", "Siyah/Yeşil Zeytin", "Reçel Çeşitleri"],
         ["Terbiyeli Şehriye Çorbası / Tarhana Çorbası", "Misket Köfte / Tavuk Külbastı+Sebze Garnitür / Mücver+Yoğurt", "Cevizli Erişte", "Çilek"]),
    _day("2026-06-09", "9 Haziran 2026 Salı",
         ["Kaşarlı Omlet", "Simit", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Ezogelin Çorbası / Kremalı Mantar Çorbası", "Tavuk Pirzola+Elma Dilim Patates / Karışık Dolma+Yoğurt", "Salçalı Makarna", "Kaşık Salata"]),
    _day("2026-06-10", "10 Haziran 2026 Çarşamba",
         ["Sosis Kokteyl (Kızartma)", "Haşlanmış Yumurta", "Tulum Peynir", "Siyah/Yeşil Zeytin", "Helva"],
         ["Mahluta Çorbası / Şafak Çorbası", "Ekmek Arası Köfte / Ratatuy", "Bulgur Pilavı", "Ayran"]),
    _day("2026-06-11", "11 Haziran 2026 Perşembe",
         ["Sade Omlet", "Dere Otlu Poğaça", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Bal+Tereyağ"],
         ["Çeşmi Nigar Çorbası / Köz Biber Çorbası", "Galeta Unlu Tavuk+Garnitür / Barbunya Yemeği", "Pirinç Pilavı", "Magnolya"]),
    _day("2026-06-12", "12 Haziran 2026 Cuma",
         ["Patates Kızartması", "Menemen", "Labne Peyniri", "Siyah/Yeşil Zeytin", "Sürülebilir Çikolata"],
         ["Salçalı Şehriye Çorbası / Sebze Çorbası", "Arnavut Ciğeri+Garnitür / Izgara Tavuk+Garnitür / Mantar Sote", "Salçalı Bulgur Pilavı", "Cacık"]),
    _day("2026-06-13", "13 Haziran 2026 Cumartesi",
         ["Sucuklu Yumurta", "Zeytinli/Peynirli Açma", "Kaşar Peynir", "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Mercimek Çorbası / Mısır Çorbası", "Lavaşta Tavuk Tantuni / Bezelye Yemeği", "Spagetti Napoliten", "Ayran"]),
    _day("2026-06-14", "14 Haziran 2026 Pazar",
         ["Karışık Pizza", "Haşlanmış Yumurta", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Tahinli Pekmez"],
         ["Düğün Çorbası / Domates Çorbası", "Nohut Yemeği / Yoğurtlu Karnabahar Kızartma", "Şehriyeli Pirinç Pilavı", "Cevizli Baklava"]),
    _day("2026-06-15", "15 Haziran 2026 Pazartesi",
         ["Peynirli Omlet", "Sade Poğaça", "Kaşar Peynir", "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Ezogelin Çorbası / Havuç Çorbası", "Lavaşta Et Tantuni / Çin Usulü Tavuk / İmam Bayıldı", "Domatesli Bulgur Pilavı", "Ayran"]),
    _day("2026-06-16", "16 Haziran 2026 Salı",
         ["Sosisli Patates Kızartması", "Haşlanmış Yumurta", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Reçel Çeşitleri"],
         ["Tarhana Çorbası / Kremalı Mantar Çorbası", "Tavuk Külbastı+Garnitür / Biber Dolma+Yoğurt", "Salçalı Makarna", "Kremalı Çikolatalı Pasta"]),
    _day("2026-06-17", "17 Haziran 2026 Çarşamba",
         ["Sade Omlet", "Simit", "Çeçil Peyniri", "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Çeşminigar Çorbası / Anadolu Çorbası", "Pideli Köfte / Soslu Karışık Kızartma", "Havuçlu Pirinç Pilavı", "Ayran"]),
    _day("2026-06-18", "18 Haziran 2026 Perşembe",
         ["Patates Salatası", "Haşlanmış Yumurta", "Kaşar Peynir", "Siyah/Yeşil Zeytin", "Muz"],
         ["Salçalı Şehriye Çorbası / Sebze Çorbası", "Galeta Unlu Tavuk+Elma Dilim Patates / Mercimek Yemeği", "Bulgur Pilavı", "Rus Salatası"]),
    _day("2026-06-19", "19 Haziran 2026 Cuma",
         ["Menemen", "Dere Otlu Poğaça", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Bal+Tereyağ"],
         ["Mercimek Çorbası / Düğün Çorbası", "Kuru Fasulye / Kabak Sandal", "Şehriyeli Pirinç Pilavı", "Yoğurt / Haşhaşlı Revani"]),
    _day("2026-06-20", "20 Haziran 2026 Cumartesi",
         ["Karışık Kızartma", "Haşlanmış Yumurta", "Kaşar Peynir", "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Domates Çorbası / Tutmaç Çorbası", "Tavuk Şiş+Garnitür / Yoğurtlu Karnabahar Kızartma", "Spagetti Napoliten", "Çiğ Köfte"]),
    _day("2026-06-21", "21 Haziran 2026 Pazar",
         ["Kaşarlı Omlet", "Patates Kroket", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Sürülebilir Çikolata"],
         ["Ezogelin Çorbası / Yayla Çorbası", "Tas Kebabı / Izgara Tavuk+Garnitür / Falafel+Yoğurt", "Salçalı Bulgur Pilavı", "Ege Salata"]),
    _day("2026-06-22", "22 Haziran 2026 Pazartesi",
         ["Patates Kızartması", "Haşlanmış Yumurta", "Kaşar Peynir", "Siyah/Yeşil Zeytin", "Reçel Çeşitleri"],
         ["Tarhana Çorbası / Kremalı Mantar Çorbası", "Tavuk Pirzola+Garnitür / Mücver+Yoğurt", "Şehriyeli Pirinç Pilavı", "Trileçe"]),
    _day("2026-06-23", "23 Haziran 2026 Salı",
         ["Sucuklu Yumurta", "Peynirli Milföy Börek", "Labne Peynir", "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Çeşminigar Çorbası / Köz Biber Çorbası", "Hamburger / Ratatuy", "Cevizli Erişte", "Ayran"]),
    _day("2026-06-24", "24 Haziran 2026 Çarşamba",
         ["Karışık Pizza", "Haşlanmış Yumurta", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Tahinli Pekmez"],
         ["Domates Çorbası / Yayla Çorbası", "Galeta Unlu Tavuk+Elma Dilim Patates", "Sebzeli Bulgur Pilavı", "Kayısı"]),
    _day("2026-06-25", "25 Haziran 2026 Perşembe",
         ["Sade Omlet", "Zeytinli/Peynirli Açma", "Örgü Peynir", "Siyah/Yeşil Zeytin", "Bal+Tereyağ"],
         ["Mercimek Çorbası / Düğün Çorbası", "Nohut Yemeği / Taze Fasulye", "Şehriyeli Pirinç Pilavı", "Cacık"]),
    _day("2026-06-26", "26 Haziran 2026 Cuma",
         ["Sosis Kokteyl (Salçalı)", "Haşlanmış Yumurta", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Salçalı Şehriye Çorbası / Yüksük Çorbası", "İzmir Köfte / Izgara Tavuk+Garnitür / İmam Bayıldı", "Şehriyeli Bulgur Pilavı", "Kakaolu Puding"]),
    _day("2026-06-27", "27 Haziran 2026 Cumartesi",
         ["Peynirli Omlet", "Sade Poğaça", "Kaşar Peynir", "Siyah/Yeşil Zeytin", "Sürülebilir Çikolata"],
         ["Ezogelin Çorbası / Anadolu Çorbası", "Lavaşta Tavuk Tantuni / Barbunya Yemeği", "Fırın Makarna", "Ayran"]),
    _day("2026-06-28", "28 Haziran 2026 Pazar",
         ["Patates Kızartması", "Haşlanmış Yumurta", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Mevsim Sebzeleri Söğüş"],
         ["Tarhana Çorbası / Havuç Çorbası", "Çoban Kavurma / Garnitürlü Tavuk Sarma / Yoğurtlu Yaz Kızartma", "Sebzeli Bulgur Pilavı", "Tahinli Cevizli Kemalpaşa Tatlısı"]),
    _day("2026-06-29", "29 Haziran 2026 Pazartesi",
         ["Menemen", "Simit", "Ezine Peynir", "Siyah/Yeşil Zeytin", "Helva"],
         ["Çeşminigar Çorbası / Sebze Çorbası", "Tavuk Pirzola+Garnitür / Karışık Dolma+Yoğurt", "Makarna (Sos Çeşitleri)", "Karışık Salata"]),
    _day("2026-06-30", "30 Haziran 2026 Salı",
         ["Patates Kavurması", "Haşlanmış Yumurta", "Beyaz Peynir", "Siyah/Yeşil Zeytin", "Reçel Çeşitleri"],
         ["Domates Çorbası / Düğün Çorbası", "Kuru Fasulye / Türlü", "Şehriyeli Pirinç Pilavı", "Mozaik Pasta / Turşu"]),
]


# ──────────────────────────────────────────────
# EYLÜL 2026
# ──────────────────────────────────────────────
_SEPTEMBER_2026 = [
    _day("2026-09-22", "22 Eylül 2026 Salı",
         ["Sade Omlet", "Sosis Kızartma", "Sade Poğaça", "Kaşar Peynir", "Siyah/Yeşil Zeytin"],
         ["Domates Çorba - Terbiyeli Şehriye Çorba", "Hünkar Beğendi (Kuşbaşı etli) / Tavuk Pirzola + Garnitür / Taze Fasulye Yemeği", "Salçalı Bulgur Pilavı", "Ezme", "Meyve Suyu / Ayran"]),
    _day("2026-09-23", "23 Eylül 2026 Çarşamba",
         ["Haşlanmış Yumurta", "Patates Kızartması", "Zeytinli/Peynirli Açma", "Beyaz Peynir", "Siyah/Yeşil Zeytin"],
         ["Mercimek Çorba - Sebze Çorba", "Tavuk Fajita / Biber Dolma + Yoğurt", "Salçalı Makarna", "Karışık Salata", "Meyve Suyu / Ayran"]),
    _day("2026-09-24", "24 Eylül 2026 Perşembe",
         ["Kaşarlı Omlet", "Karışık Kızartma", "Peynirli Milföy Börek", "Tulum Peynir", "Siyah/Yeşil Zeytin"],
         ["Düğün Çorba - Havuç Çorba", "Nohut Yemeği / Mücver + Yoğurt", "Domatesli Bulgur Pilavı", "Cevizli Baklava", "Meyve Suyu / Ayran"]),
    _day("2026-09-25", "25 Eylül 2026 Cuma",
         ["Haşlanmış Yumurta", "Patates Salatası", "Pankek + Bal", "Kaşar Peynir", "Siyah/Yeşil Zeytin"],
         ["Tavuk Çorba - Şafak Çorba", "Mengen Musakka / Sebze Graten", "Şehriyeli Pirinç Pilavı", "Cacık", "Meyve Suyu / Ayran"]),
    _day("2026-09-26", "26 Eylül 2026 Cumartesi",
         ["Menemen", "Salçalı Sosis", "Simit", "Krem Peynir", "Siyah/Yeşil Zeytin"],
         ["Tarhana Çorba - Salçalı Şehriye Çorba", "Galeta Unlu Tavuk + Garnitür / Bezelye Yemeği", "Cevizli Erişte", "Havuç Tarator", "Meyve Suyu / Ayran"]),
    _day("2026-09-27", "27 Eylül 2026 Pazar",
         ["Haşlanmış Yumurta", "Patates Kızartması", "Peynirli/Ispanaklı Börek", "Örgü Peynir", "Siyah/Yeşil Zeytin"],
         ["Ezogelin Çorba - Yayla Çorba", "Orman Kebabı / Beşamel Soslu Tavuk / Karnabahar Kızartma + Yoğurt", "Sebzeli Bulgur Pilavı", "Aysberg Salata", "Meyve Suyu / Ayran"]),
    _day("2026-09-28", "28 Eylül 2026 Pazartesi",
         ["Sucuklu Yumurta", "Patates Kavurması", "Dere Otlu Poğaça", "Beyaz Peynir", "Siyah/Yeşil Zeytin"],
         ["Mercimek Çorba - Terbiyeli Şehriye Çorba", "Hamburger / Mantar Sote", "Patates Kızartması + Ketçap + Mayonez", "Çiğköfte", "Meyve Suyu / Ayran"]),
    _day("2026-09-29", "29 Eylül 2026 Salı",
         ["Haşlanmış Yumurta", "Karışık Kızartma", "Tepsi Böreği", "Kaşar Peynir", "Siyah/Yeşil Zeytin"],
         ["Tarhana Çorba - Kremalı Mantar Çorba", "Izgara Tavuk + Garnitür / Biber Dolma", "Spagetti Napoliten", "Yoğurt", "Meyve Suyu / Ayran"]),
    _day("2026-09-30", "30 Eylül 2026 Çarşamba",
         ["Peynirli Omlet", "Salçalı Sosis", "Sade Poğaça", "Beyaz Peynir", "Siyah/Yeşil Zeytin"],
         ["Toyga Çorba - Domates Çorba", "Et Fajita + Lavaş / Tavuk Sote / Taze Fasulye", "Domatesli Bulgur Pilavı", "Tiramisu", "Meyve Suyu / Ayran"]),
]


_OCTOBER_2026 = [
    _day("2026-10-01", "1 Ekim 2026 Perşembe", ['Haşlanmış Yumurta (1 adet L boy)', 'Patates Kavurması 150 g', 'Karışık Pizza 150 g', 'Krem Peynir 20 g'], ['Ezogelin Çorba - Salçalı Şehriye Çorba', 'Tavuk Şiş+Garnitür - Mücver+Yoğurt (200 g (100 g et)', '200 g)', 'Makarna (Sos Çeşitleri ile) 200 g', 'Çoban Salata 150 g'], total_calories_breakfast=880, total_calories_dinner=950),
    _day("2026-10-02", "2 Ekim 2026 Cuma", ['Menemen 150 g (1 adet L boy yumurta)', 'Patates Kızartması 150 g', 'Çikolatalı Milföy Börek 60 g', 'Beyaz Peynir 40 g'], ['Düğün Çorba - Şafak Çorba', 'Kuru Fasulye - Sebze Graten (200 g', '200 g)', 'Pirinç Pilavı 150 g', 'Cacık 150 g', 'Supangle 150 g'], total_calories_breakfast=900, total_calories_dinner=850),
    _day("2026-10-03", "3 Ekim 2026 Cumartesi", ['Haşlanmış Yumurta', 'Karışık Kızartma 150 g', 'Simit 1 adet', 'Kaşar Peyniri 40 g'], ['Mercimek Çorba - Sebze Çorba', 'Çoban Kavurma - Köri Soslu Tavuk - Bezelye Yemeği (%40-%40-%20)', 'Bulgur Pilavı 200 g', 'Ayran 170-200 ml'], total_calories_breakfast=920, total_calories_dinner=900),
    _day("2026-10-04", "4 Ekim 2026 Pazar", ['Sade Omlet (1 adet L boy yumurta', '70 g)', 'Salçalı Sosis 100 g', 'Peynirli/Ispanaklı Börek 120 g', 'Beyaz Peynir 40 g'], ['Domates Çorba - Terbiyeli Şehriye Çorba', 'Tavuk Külbastı+Garnitür - Biber Dolma+Yoğurt (%70-%30)', 'Spagetti Napoliten 200 g', 'Karışık Salata 100 g'], total_calories_breakfast=880, total_calories_dinner=890),
    _day("2026-10-05", "5 Ekim 2026 Pazartesi", ['Haşlanmış Yumurta', 'Patates Kızartması 150 g', 'Zeytinli/Peynirli Açma 1 adet', 'Kaşar Peyniri 40 g'], ['Ezogelin Çorba - Kremalı Mantar Çorba', 'Karnıyarık - Taze Fasulye (200 g (60 g et)', '200 g)', 'Şehriyeli Pirinç Pilavı 150 g', 'Cacık 150 g'], total_calories_breakfast=900, total_calories_dinner=880),
    _day("2026-10-06", "6 Ekim 2026 Salı", ['Kaşarlı Omlet (25 g kaşar + 1 adet L boy yumurta', '100 g)', 'Patates Salatası 150 g', 'Dere Otlu Poğaça 1 adet', 'Labne Peynir 20 g'], ['Tarhana Çorba - Havuç Çorba', 'Galeta Unlu Tavuk+Garnitür - Yeşil Mercimek Yemeği (%90-%10)', 'Sebzeli Bulgur Pilavı 200 g', 'Kremşantili Haşhaşlı Revani 100 g'], total_calories_breakfast=890, total_calories_dinner=910),
    _day("2026-10-07", "7 Ekim 2026 Çarşamba", ['Haşlanmış Yumurta', 'Sosis Kızartma 100 g', 'Peynirli/Ispanaklı Börek 120 g', 'Beyaz Peynir 40 g'], ['Yayla Çorba - Mercimek Çorba', 'Izgara Köfte+Garnitür - Izgara Tavuk+Garnitür - Mücver+Yoğurt (%40-%40-%20)', 'Salçalı Makarna 200 g', 'Trileçe 150 g'], total_calories_breakfast=880, total_calories_dinner=930),
    _day("2026-10-08", "8 Ekim 2026 Perşembe", ['Sucuklu Omlet (1 adet L boy yumurta + 25 g beyaz etli sucuk', '100 g)', 'Kekikli Domates Biber Kızartma 100 g', 'Kakaolu Kek 50 g', 'Ezine Peyniri 40 g'], ['Salçalı Şehriye Çorba - Toyga Çorba', 'Tavuk Fajita - Patates Oturtma - Sebze Graten (%40-%40-%20)', 'Pirinç Pilavı 150 g', 'Kaşık Salata 150 g'], total_calories_breakfast=870, total_calories_dinner=910),
    _day("2026-10-09", "9 Ekim 2026 Cuma", ['Haşlanmış Yumurta', 'Patates Kızartması 150 g', 'Simit 1 adet', 'Beyaz Peynir 40 g'], ['Mahluta Çorba - Köz Biber Çorba', 'Hünkâr Beğendi (kuşbaşı etli) - Tavuk Pirzola+Garnitür - Bezelye Yemeği (%40-%40-%20)', 'Bulgur Pilavı 200 g', 'Haydari 100 g'], total_calories_breakfast=910, total_calories_dinner=900),
    _day("2026-10-10", "10 Ekim 2026 Cumartesi", ['Peynirli Omlet (30 g beyaz peynir + 1 adet L boy yumurta', '100 g)', 'Patates Kavurması 150 g', 'Sosisli Milföy Börek 60 g', 'Kaşar Peyniri 40 g'], ['Ezogelin Çorba - Sebze Çorba', 'Tavuk Külbastı+Garnitür - Biber Dolma+Yoğurt (%70-%30)', 'Cevizli Erişte 200 g', 'Ege Salata 150 g'], total_calories_breakfast=880, total_calories_dinner=890),
    _day("2026-10-11", "11 Ekim 2026 Pazar", ['Haşlanmış Yumurta', 'Patates Kroket 60 g', 'Karışık Pizza 150 g', 'Beyaz Peynir 40 g'], ['Tarhana Çorba - Düğün Çorba', 'Nohut Yemeği - İmam Bayıldı (200 g', '200 g)', 'Şehriyeli Pirinç Pilavı 150 g', 'Cevizli Baklava 100 g'], total_calories_breakfast=870, total_calories_dinner=850),
    _day("2026-10-12", "12 Ekim 2026 Pazartesi", ['Sade Omlet (70 g)', 'Patates Kızartması 150 g', 'Çikolatalı Milföy Börek 60 g', 'Kaşar Peyniri 40 g'], ['Mercimek Çorba - Kremalı Mantar Çorba', 'Tas Kebabı - Beşamel Soslu Tavuk - Karnabahar Kızartma+Yoğurt (%40-%40-%20)', 'Salçalı Bulgur Pilavı 200 g', 'Havuç Aysberg Salata 100 g'], total_calories_breakfast=900, total_calories_dinner=910),
    _day("2026-10-13", "13 Ekim 2026 Salı", ['Haşlanmış Yumurta', 'Salçalı Sosis 100 g', 'Sade Poğaça 1 adet', 'Çeçil Peyniri 40 g'], ['Çeşmi Nigar Çorba - Salçalı Şehriye Çorba', 'Izgara Tavuk+Garnitür - Patlıcan Musakka - Barbunya Yemeği (%50-%30-%20)', 'Pirinç Pilavı 150 g', 'Çikolatalı Kremalı Pasta 120 g'], total_calories_breakfast=850, total_calories_dinner=930),
    _day("2026-10-14", "14 Ekim 2026 Çarşamba", ['Kaşarlı Omlet (25 g kaşar + 1 yumurta', '100 g)', 'Karışık Kızartma 150 g', 'Zeytinli/Peynirli Açma 1 adet', 'Beyaz Peynir 40 g'], ['Tarhana Çorba - Havuç Çorba', 'Hamburger - Taze Fasulye (%90-%10)', 'Patates Kızartması+Ketçap+Mayonez 150 g', 'Ayran veya Meyve Suyu 170-200 ml'], total_calories_breakfast=910, total_calories_dinner=950),
    _day("2026-10-15", "15 Ekim 2026 Perşembe", ['Haşlanmış Yumurta', 'Patates Salatası 150 g', 'Pankek + Sürülebilir Çikolata (2 adet + 20 g)', 'Kaşar Peyniri 40 g'], ['Yayla Çorba - Ezogelin Çorba', 'Galeta Unlu Tavuk+Garnitür - Türlü Yemeği (%90-%10)', 'Sebzeli Bulgur Pilavı 200 g', 'Çoban Salata 150 g'], total_calories_breakfast=880, total_calories_dinner=930),
    _day("2026-10-16", "16 Ekim 2026 Cuma", ['Menemen 150 g (1 adet L boy yumurta)', 'Patates Kızartması 150 g', 'Simit 1 adet', 'Krem Peynir 20 g'], ['Düğün Çorba - Domates Çorba', 'Kuru Fasulye - Sebze Graten', 'Şehriyeli Pirinç Pilavı 150 g', 'Cacık 150 g', 'Fındıklı Şekerpare 100 g'], total_calories_breakfast=900, total_calories_dinner=900),
    _day("2026-10-17", "17 Ekim 2026 Cumartesi", ['Haşlanmış Yumurta', 'Salçalı Sosis 100 g', 'Peynirli/Ispanaklı Börek 120 g', 'Tulum Peyniri 40 g'], ['Terbiyeli Şehriye Çorba - Mahluta Çorba', 'Lavaşta Tavuk Tantuni - Bezelye Yemeği (%90-%10)', 'Spagetti Napoliten 200 g', 'Ayran 170-200 ml'], total_calories_breakfast=890, total_calories_dinner=910),
    _day("2026-10-18", "18 Ekim 2026 Pazar", ['Sucuklu Omlet (1 yumurta + 25 g beyaz etli sucuk', '100 g)', 'Patates Kavurması 150 g', 'Pişi + Reçel (120 g + 20 g)', 'Beyaz Peynir 40 g'], ['Mercimek Çorba - Köz Biber Çorba', 'Orman Kebabı - Tavuk Şiş+Garnitür - Kabak Sandal (%40-%40-%20)', 'Bulgur Pilavı 200 g', 'Havuç Tarator 100 g'], total_calories_breakfast=920, total_calories_dinner=920),
    _day("2026-10-19", "19 Ekim 2026 Pazartesi", ['Haşlanmış Yumurta', 'Sosis Kızartma 100 g', 'Dereotlu Poğaça 1 adet', 'Kaşar Peyniri 40 g'], ['Tarhana Çorba - Yayla Çorba', 'Tavuk Fajita - Karnabahar Kızartma+Yoğurt', 'Makarna (Sos Çeşitleri ile) 200 g', 'Cevizli Baklava 100 g'], total_calories_breakfast=890, total_calories_dinner=930),
    _day("2026-10-20", "20 Ekim 2026 Salı", ['Peynirli Omlet (30 g beyaz peynir + 1 yumurta', '100 g)', 'Patates Kroket 60 g', 'Karışık Pizza 150 g', 'Beyaz Peynir 40 g'], ['Çeşmi Nigar Çorba - Salçalı Şehriye Çorba', 'Biga Köfte+Garnitür - Tavuk Külbastı+Garnitür - Mantar Sote (%40-%40-%20)', 'Pirinç Pilavı 150 g', 'Cacık 150 g'], total_calories_breakfast=880, total_calories_dinner=910),
    _day("2026-10-21", "21 Ekim 2026 Çarşamba", ['Haşlanmış Yumurta', 'Patates Kızartması 150 g', 'Sade Poğaça 1 adet', 'Labne Peynir 20 g'], ['Sebze Çorba - Ezogelin Çorba', 'Köri Soslu Tavuk - Mücver+Yoğurt', 'Spagetti Napoliten 200 g', 'Karışık Salata 100 g'], total_calories_breakfast=880, total_calories_dinner=900),
    _day("2026-10-22", "22 Ekim 2026 Perşembe", ['Sade Omlet (70 g)', 'Patates Salatası 150 g', 'Çikolatalı Milföy Börek 60 g', 'Kaşar Peyniri 40 g'], ['Domates Çorba - Düğün Çorba', 'Nohut Yemeği - Taze Fasulye (200 g', '200 g)', 'Domatesli Bulgur Pilavı 200 g', 'Ezme 100 g', 'Sütlaç 150 g'], total_calories_breakfast=900, total_calories_dinner=890),
    _day("2026-10-23", "23 Ekim 2026 Cuma", ['Haşlanmış Yumurta', 'Patates Kızartması 150 g', 'Peynirli/Ispanaklı Börek 120 g', 'Beyaz Peynir 40 g'], ['Mercimek Çorba - Havuç Çorba', 'Misket Köfte - Tavuk Sote - Türlü (%40-%40-%20)', 'Cevizli Erişte 200 g', 'Kaşık Salata 150 g'], total_calories_breakfast=850, total_calories_dinner=910),
    _day("2026-10-24", "24 Ekim 2026 Cumartesi", ['Kaşarlı Omlet (25 g kaşar + 1 yumurta', '100 g)', 'Karışık Kızartma 150 g', 'Simit 1 adet', 'Ezine Peyniri 40 g'], ['Tarhana Çorba - Kremalı Mantar Çorba', 'Galeta Unlu Tavuk+Garnitür - Bezelye Yemeği (%90-%10)', 'Şehriyeli Pirinç Pilavı 150 g', 'Çiğköfte 100 g'], total_calories_breakfast=900, total_calories_dinner=940),
    _day("2026-10-25", "25 Ekim 2026 Pazar", ['Haşlanmış Yumurta', 'Patates Kroket 60 g', 'Yumurtalı Ekmek (2 dilim tost ekmeği)', 'Beyaz Peynir 40 g'], ['Çeşmi Nigar Çorba - Köz Biber Çorba', 'Çökertme Kebabı - Tavuk Pirzola+Garnitür - Falafel+Yoğurt (%40-%40-%20)', 'Bulgur Pilavı 200 g', 'Kalburabastı 100 g'], total_calories_breakfast=920, total_calories_dinner=920),
    _day("2026-10-26", "26 Ekim 2026 Pazartesi", ['Mantarlı Omlet (30 g pişmiş mantar + 1 yumurta', '100 g)', 'Patates Salatası 150 g', 'Dere Otlu Poğaça 1 adet', 'Krem Peynir 20 g'], ['Ezogelin Çorba - Sebze Çorba', 'Izgara Tavuk+Garnitür - Püreli Et Sote - Biber Dolma+Yoğurt (%40-%30-%30)', 'Salçalı Makarna 200 g', 'Havuç Aysberg Salata 100 g'], total_calories_breakfast=890, total_calories_dinner=930),
    _day("2026-10-27", "27 Ekim 2026 Salı", ['Haşlanmış Yumurta', 'Patates Kızartması 150 g', 'Peynirli/Ispanaklı Börek 120 g', 'Beyaz Peynir 40 g'], ['Düğün Çorba - Tarhana Çorba', 'Kuru Fasulye - Sebze Graten (200 g', '200 g)', 'Pirinç Pilavı 150 g', 'Yoğurt 120 g', 'Tiramisu 120 g'], total_calories_breakfast=880, total_calories_dinner=900),
    _day("2026-10-28", "28 Ekim 2026 Çarşamba", ['Sucuklu Omlet (1 yumurta + 25 g beyaz etli sucuk', '100 g)', 'Patates Kavurması 150 g', 'Zeytinli/Peynirli Açma 1 adet', 'Kaşar Peyniri 40 g'], ['Mercimek Çorba - Anadolu Çorba', 'Et Fajita+Lavaş - Tavuk Fajita+Lavaş - Karnabahar Kızartma+Yoğurt (%40-%30-%30)', 'Sebzeli Bulgur Pilavı 200 g', 'Çoban Salata 150 g'], total_calories_breakfast=900, total_calories_dinner=920),
    _day("2026-10-29", "29 Ekim 2026 Perşembe", ['Menemen 150 g (1 adet L boy yumurta)', 'Sosis Kızartma 100 g', 'Basma Pide 120 g', 'Beyaz Peynir 40 g'], ['Domates Çorba - Yayla Çorba', 'Tavuk Sarma - Taze Fasulye', 'Makarna (Sos Çeşitleri ile) 200 g', 'Haydari 100 g'], total_calories_breakfast=890, total_calories_dinner=910),
    _day("2026-10-30", "30 Ekim 2026 Cuma", ['Sade Omlet (70 g)', 'Patates Kroket 60 g', 'Simit 1 adet', 'Çeçil Peyniri 40 g'], ['Tavuk Çorba - Çeşmi Nigar Çorba', 'Hamburger - İmam Bayıldı (%90-%10)', 'Patates Kızartması+Ketçap+Mayonez 150 g', 'Ayran veya Meyve Suyu 170-200 ml'], total_calories_breakfast=880, total_calories_dinner=950),
    _day("2026-10-31", "31 Ekim 2026 Cumartesi", ['Haşlanmış Yumurta', 'Salçalı Sosis 100 g', 'Peynirli/Ispanaklı Börek 120 g', 'Kaşar Peyniri 40 g'], ['Salçalı Şehriye Çorba - Yüksük Çorba', 'Püreli Et Sote - Püreli Tavuk Sote - Barbunya Yemeği (%40-%40-%20)', 'Şehriyeli Pirinç Pilavı 150 g', 'Supangle 150 g'], total_calories_breakfast=860, total_calories_dinner=930),
]

MANUAL_MENUS = {
    "2026-10": _OCTOBER_2026,
    "2026-05": _MAY_2026,
    "2026-06": _JUNE_2026,
    "2026-09": _SEPTEMBER_2026,
}
