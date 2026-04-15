import httpx
from bs4 import BeautifulSoup
from typing import Dict, Optional
from datetime import datetime, timedelta

# Cache için
def _minutes_until_midnight() -> int:
    """Gece yarısına kadar kalan dakika sayısını döndürür (minimum 1 dakika)"""
    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(1, int((midnight - now).total_seconds() / 60))

class BusCache:
    def __init__(self):
        self._data: Optional[Dict] = None
        self._expires: Optional[datetime] = None
        self._cached_date: Optional[str] = None

    def get(self) -> Optional[Dict]:
        today = datetime.now().strftime("%Y-%m-%d")
        if self._data and self._expires and datetime.now() < self._expires and self._cached_date == today:
            return self._data
        return None

    def set(self, data: Dict):
        self._data = data
        self._cached_date = datetime.now().strftime("%Y-%m-%d")
        self._expires = datetime.now() + timedelta(minutes=_minutes_until_midnight())

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
    
    async def get_bus_schedule(self) -> Dict:
        """Haftaiçi ve haftasonu otobüs saatleri PDF'lerini döndürür"""
        
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
                        text_normalized = remove_diacritics(text).lower()
                        all_pdfs.append({
                            'url': href,
                            'text': text,
                            'text_lower': text_normalized
                        })
                        print(f"PDF Bulundu: {text} -> {href}")
                
                result = {
                    "weekday": None,
                    "weekend": None,
                    "last_update": datetime.now().isoformat(),
                    "source": "Çanakkale Belediyesi"
                }
                
                # PDF'leri türüne göre kategorize et (bugüne özel olanları önceliklendir)
                weekday_candidates = []
                weekend_candidates = []
                for pdf in all_pdfs:
                    text_lower = pdf['text_lower']
                    url = self._make_absolute_url(pdf['url'])
                    is_today_specific = self._is_today_specific_pdf(pdf['text'], url)
                    
                    # Haftaiçi - "hafta içi" veya "ici" içerir ve "sonu" yok
                    if ('hafta' in text_lower and 'ici' in text_lower) or ('ici' in text_lower and 'sonu' not in text_lower):
                        weekday_candidates.append({
                            "url": url,
                            "label": pdf['text'] or "Haftaiçi Saatleri",
                            "is_today": is_today_specific
                        })
                    # Haftasonu - "sonu" veya "hafta sonu" içerir
                    elif 'sonu' in text_lower:
                        weekend_candidates.append({
                            "url": url,
                            "label": pdf['text'] or "Haftasonu Saatleri",
                            "is_today": is_today_specific
                        })

                # Bugüne özel PDF varsa onu, yoksa listedeki ilk uygun PDF'i seç
                if weekday_candidates:
                    result["weekday"] = next(
                        (item for item in weekday_candidates if item["is_today"]),
                        weekday_candidates[0]
                    )
                    result["weekday"].pop("is_today", None)

                if weekend_candidates:
                    result["weekend"] = next(
                        (item for item in weekend_candidates if item["is_today"]),
                        weekend_candidates[0]
                    )
                    result["weekend"].pop("is_today", None)
                
                # Eğer hiç bulunamadıysa, fallback kullan
                if not result["weekday"] and not result["weekend"]:
                    print("BUS: PDF bulunamadı, fallback kullanılıyor")
                    return self._get_fallback()
                
                # Cache'e kaydet (gece yarısına kadar)
                cache.set(result)
                print(f"BUS: Siteden çekildi - Weekday: {result['weekday']}, Weekend: {result['weekend']}")
                
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
        """Fallback veri - güncel PDF linkleri"""
        return {
            "weekday": {
                "url": "https://ulasim.canakkale.bel.tr/wp-content/uploads/2018/02/19-OCAK-11.pdf",
                "label": "Haftaiçi Sefer Saatleri"
            },
            "weekend": {
                "url": "https://ulasim.canakkale.bel.tr/wp-content/uploads/2018/02/17-OCAK-7.pdf",
                "label": "Haftasonu Sefer Saatleri"
            },
            "last_update": datetime.now().isoformat(),
            "source": "Çanakkale Belediyesi"
        }

bus_service = BusService()
