import httpx
from bs4 import BeautifulSoup
from typing import Dict, Optional
from datetime import datetime, timedelta, date

BUS_CACHE_TTL = timedelta(seconds=43200)

class BusCache:
    def __init__(self):
        self._data: Optional[Dict] = None
        self._expires: Optional[datetime] = None

    def get(self) -> Optional[Dict]:
        if self._data and self._expires and datetime.now() < self._expires:
            return self._data
        return None

    def set(self, data: Dict):
        self._data = data
        self._expires = datetime.now() + BUS_CACHE_TTL

cache = BusCache()

def remove_diacritics(text: str) -> str:
    """Türkçe karakterleri ASCII'ye çevir"""
    replacements = {
        'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G',
        'ü': 'u', 'Ü': 'U', 'ş': 's', 'Ş': 'S',
        'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'
    }
    for tr, en in replacements.items():
        text = text.replace(tr, en)
    return text

class BusService:
    BUS_URL = "https://ulasim.canakkale.bel.tr/rehber/hatlar-otobus-saatleri/"

    @staticmethod
    def _get_today_date_tokens() -> list[str]:
        """Bugünün tarihini farklı metin formatlarıyla döndürür."""
        now = datetime.now()
        day = now.day
        month = now.month
        month_names = {
            1: "ocak", 2: "subat", 3: "mart", 4: "nisan", 5: "mayis", 6: "haziran",
            7: "temmuz", 8: "agustos", 9: "eylul", 10: "ekim", 11: "kasim", 12: "aralik"
        }
        month_name = month_names[month]
        day_2 = f"{day:02d}"
        month_2 = f"{month:02d}"

        return [
            f"{day} {month_name}",
            f"{day_2} {month_name}",
            f"{day}.{month}",
            f"{day_2}.{month}",
            f"{day}.{month_2}",
            f"{day_2}.{month_2}",
            f"{day}/{month}",
            f"{day_2}/{month}",
            f"{day}/{month_2}",
            f"{day_2}/{month_2}",
            f"{day}-{month}",
            f"{day_2}-{month}",
            f"{day}-{month_2}",
            f"{day_2}-{month_2}",
        ]

    def _is_today_specific_pdf(self, text: str, url: str) -> bool:
        """PDF başlığı veya URL'inde bugünün tarihinin geçip geçmediğini kontrol eder."""
        haystack = remove_diacritics(f"{text} {url}").lower()
        return any(token in haystack for token in self._get_today_date_tokens())
    
    def _is_special_day_pdf(self, text: str) -> bool:
        """PDF'in güne özel (tatil, özel gün vb.) olup olmadığını kontrol eder.
        Sadece tarih + özel gün anahtar kelimesi içeren PDF'ler kabul edilir.
        Örn: '1 MAYIS GÜNÜ SEFER SAATLERİ' → True
        Örn: '4 MAYIS İTİBARİYLE HAFTA İÇİ SEFER SAATLERİ' → False
        """
        text_lower = remove_diacritics(text).lower()
        # Hafta içi veya hafta sonu ise özel gün değil
        if ('hafta' in text_lower and 'ici' in text_lower) or 'sonu' in text_lower:
            return False
        # "itibariyle/itibari ile" içeren PDF'ler gelecek tarihli güncelleme, özel gün değil
        if 'itibariyle' in text_lower or 'itibari' in text_lower:
            return False
        # Tarih kalıbı ("1 mayis") VE özel gün anahtar kelimesi ("günü/tatil/bayram") ZORUNLU
        import re
        has_date = bool(re.search(r'\d{1,2}\s*(?:ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik)', text_lower))
        special_keywords = ['gunu', 'ozel', 'tatil', 'bayram', 'resmi']
        has_special_keyword = any(kw in text_lower for kw in special_keywords)
        return has_date and has_special_keyword

    def _extract_short_date_label(self, text: str) -> str:
        """PDF başlığından kısa tarih etiketi çıkarır.
        '1 MAYIS GÜNÜ SEFER SAATLERİ' → '1 Mayıs'
        '19 MAYIS GÜNÜ SEFER SAATLERİ' → '19 Mayıs'
        """
        import re
        text_ascii = remove_diacritics(text).lower()
        month_map = {
            'ocak': 'Ocak', 'subat': 'Şubat', 'mart': 'Mart', 'nisan': 'Nisan',
            'mayis': 'Mayıs', 'haziran': 'Haziran', 'temmuz': 'Temmuz',
            'agustos': 'Ağustos', 'eylul': 'Eylül', 'ekim': 'Ekim',
            'kasim': 'Kasım', 'aralik': 'Aralık'
        }
        match = re.search(r'(\d{1,2})\s*(ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik)', text_ascii)
        if match:
            day = match.group(1)
            month_key = match.group(2)
            return f"{day} {month_map.get(month_key, month_key.title())}"
        return text

    def _is_itibariyle_pdf(self, text: str) -> bool:
        """'X tarih itibariyle' formatındaki güncellenmiş PDF'leri tespit eder."""
        text_lower = remove_diacritics(text).lower()
        return 'itibariyle' in text_lower or 'itibari' in text_lower

    def _extract_date_from_text(self, text: str) -> Optional[date]:
        """Metinden tarih (gun/ay) yakalar; yil yoksa bu yil varsayilir."""
        import re
        text_ascii = remove_diacritics(text).lower()
        month_map = {
            'ocak': 1, 'subat': 2, 'mart': 3, 'nisan': 4,
            'mayis': 5, 'haziran': 6, 'temmuz': 7, 'agustos': 8,
            'eylul': 9, 'ekim': 10, 'kasim': 11, 'aralik': 12
        }

        match = re.search(r'(\d{1,2})\s*(ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik)', text_ascii)
        if match:
            day = int(match.group(1))
            month = month_map.get(match.group(2))
            if month:
                return date(datetime.now().year, month, day)

        numeric = re.search(r'(\d{1,2})[./-](\d{1,2})(?:[./-](\d{2,4}))?', text_ascii)
        if numeric:
            day = int(numeric.group(1))
            month = int(numeric.group(2))
            year = numeric.group(3)
            if year:
                year_val = int(year)
                if year_val < 100:
                    year_val += 2000
            else:
                year_val = datetime.now().year
            return date(year_val, month, day)

        return None

    def _is_itibariyle_effective(self, text: str, url: str) -> bool:
        """'itibariyle' PDF'i bugun veya gecmis tarihliyse gecerli sayar."""
        effective_date = self._extract_date_from_text(f"{text} {url}")
        if not effective_date:
            return True
        return effective_date <= datetime.now().date()

    async def get_bus_schedule(self) -> Dict:
        """Belediye sitesindeki tum otobus PDF'lerini dondurur"""
        
        # Cache kontrol
        cached = cache.get()
        if cached:
            print("BUS: Cache'den döndü")
            return cached
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.BUS_URL, headers=headers, timeout=10.0)
                
                if response.status_code != 200:
                    print(f"BUS: HTTP Hatası {response.status_code}")
                    return self._get_fallback()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Tüm PDF linklerini topla
                all_pdfs = []
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    
                    if '.pdf' in href.lower():
                        all_pdfs.append({
                            'url': href,
                            'text': text
                        })
                        print(f"PDF Bulundu: {text} -> {href}")
                
                result = {
                    "pdfs": [],
                    "last_update": datetime.now().isoformat(),
                    "source": "Çanakkale Belediyesi"
                }

                for pdf in all_pdfs:
                    url = self._make_absolute_url(pdf['url'])
                    label = pdf['text'] or url.split('/')[-1]
                    result["pdfs"].append({
                        "url": url,
                        "label": label
                    })

                if not result["pdfs"]:
                    print("BUS: PDF bulunamadı, fallback kullanılıyor")
                    return self._get_fallback()

                cache.set(result)
                print(f"BUS: Siteden çekildi - PDF sayisi: {len(result['pdfs'])}")
                return result
                
        except Exception as e:
            print(f"BUS Scraping Hatası: {e}")
            return self._get_fallback()
    
    def _make_absolute_url(self, url: str) -> str:
        """Relative URL'i absolute yap"""
        if url.startswith('http'):
            return url
        if url.startswith('/'):
            return f"https://ulasim.canakkale.bel.tr{url}"
        return f"https://ulasim.canakkale.bel.tr/{url}"
    
    def _get_fallback(self) -> Dict:
        """Fallback veri - guncel PDF linkleri"""
        return {
            "pdfs": [
                {
                    "url": "https://ulasim.canakkale.bel.tr/wp-content/uploads/2018/02/19-OCAK-11.pdf",
                    "label": "Haftaiçi Sefer Saatleri"
                },
                {
                    "url": "https://ulasim.canakkale.bel.tr/wp-content/uploads/2018/02/17-OCAK-7.pdf",
                    "label": "Haftasonu Sefer Saatleri"
                }
            ],
            "last_update": datetime.now().isoformat(),
            "source": "Çanakkale Belediyesi"
        }

bus_service = BusService()
