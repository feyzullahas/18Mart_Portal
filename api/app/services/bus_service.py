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

    async def get_bus_schedule(self) -> Dict:
        """Haftaiçi, haftasonu ve güne özel otobüs saatleri PDF'lerini döndürür"""
        
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
                    "special": None,
                    "last_update": datetime.now().isoformat(),
                    "source": "Çanakkale Belediyesi"
                }
                
                # PDF'leri türüne göre kategorize et
                weekday_candidates = []
                weekend_candidates = []
                special_candidates = []
                
                for pdf in all_pdfs:
                    text_lower = pdf['text_lower']
                    url = self._make_absolute_url(pdf['url'])
                    is_today_specific = self._is_today_specific_pdf(pdf['text'], url)
                    is_special = self._is_special_day_pdf(pdf['text'])
                    is_itibariyle = self._is_itibariyle_pdf(pdf['text'])
                    
                    # Güne özel PDF (tatil, bayram vb.) — bugünün tarihini içeriyorsa
                    if is_special and is_today_specific:
                        special_candidates.append({
                            "url": url,
                            "label": self._extract_short_date_label(pdf['text']),
                        })
                        print(f"  -> ÖZEL GÜN PDF (bugüne ait): {pdf['text']}")
                        continue
                    
                    # "İtibariyle" PDF'ler — hafta içi güncelleme (yeni tarihten itibaren geçerli)
                    if is_itibariyle:
                        if 'ici' in text_lower or ('sonu' not in text_lower):
                            weekday_candidates.insert(0, {
                                "url": url,
                                "label": pdf['text'] or "Haftaiçi Saatleri",
                                "is_today": is_today_specific,
                                "is_itibariyle": True
                            })
                        elif 'sonu' in text_lower:
                            weekend_candidates.insert(0, {
                                "url": url,
                                "label": pdf['text'] or "Haftasonu Saatleri",
                                "is_today": is_today_specific,
                                "is_itibariyle": True
                            })
                        continue
                    
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

                # Bugüne özel PDF varsa onu seç
                if special_candidates:
                    result["special"] = special_candidates[0]
                    print(f"  -> Bugüne özel PDF bulundu: {result['special']['label']}")

                # Hafta içi: bugüne özel olan veya itibariyle olan veya ilk uygun
                if weekday_candidates:
                    result["weekday"] = next(
                        (item for item in weekday_candidates if item.get("is_today")),
                        weekday_candidates[0]
                    )
                    result["weekday"].pop("is_today", None)
                    result["weekday"].pop("is_itibariyle", None)

                if weekend_candidates:
                    result["weekend"] = next(
                        (item for item in weekend_candidates if item.get("is_today")),
                        weekend_candidates[0]
                    )
                    result["weekend"].pop("is_today", None)
                    result["weekend"].pop("is_itibariyle", None)
                
                # Eğer hiç bulunamadıysa, fallback kullan
                if not result["weekday"] and not result["weekend"]:
                    print("BUS: PDF bulunamadı, fallback kullanılıyor")
                    return self._get_fallback()
                
                # Cache'e kaydet (gece yarısına kadar)
                cache.set(result)
                print(f"BUS: Siteden çekildi - Weekday: {result['weekday']}, Weekend: {result['weekend']}, Special: {result['special']}")
                
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
            "special": None,
            "last_update": datetime.now().isoformat(),
            "source": "Çanakkale Belediyesi"
        }

bus_service = BusService()
