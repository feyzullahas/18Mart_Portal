import httpx
from bs4 import BeautifulSoup
from typing import Dict, Optional
from datetime import datetime, timedelta

# Cache için
class BusCache:
    def __init__(self):
        self._data: Optional[Dict] = None
        self._expires: Optional[datetime] = None
    
    def get(self) -> Optional[Dict]:
        if self._data and self._expires and datetime.now() < self._expires:
            return self._data
        return None
    
    def set(self, data: Dict, ttl_hours: int = 24):
        self._data = data
        self._expires = datetime.now() + timedelta(hours=ttl_hours)

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
                response = await client.get(self.BUS_URL, headers=headers, timeout=15.0)
                
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
                
                # PDF'leri türüne göre kategorize et
                for pdf in all_pdfs:
                    text_lower = pdf['text_lower']
                    url = self._make_absolute_url(pdf['url'])
                    
                    # Haftaiçi - "hafta içi" veya "ici" içerir ve "sonu" yok
                    if ('hafta' in text_lower and 'ici' in text_lower) or ('ici' in text_lower and 'sonu' not in text_lower):
                        if not result["weekday"]:
                            result["weekday"] = {
                                "url": url,
                                "label": pdf['text'] or "Haftaiçi Saatleri"
                            }
                    # Haftasonu - "sonu" veya "hafta sonu" içerir
                    elif 'sonu' in text_lower:
                        if not result["weekend"]:
                            result["weekend"] = {
                                "url": url,
                                "label": pdf['text'] or "Haftasonu Saatleri"
                            }
                
                # Eğer hiç bulunamadıysa, fallback kullan
                if not result["weekday"] and not result["weekend"]:
                    print("BUS: PDF bulunamadı, fallback kullanılıyor")
                    return self._get_fallback()
                
                # Cache'e kaydet (24 saat)
                cache.set(result, 24)
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
