import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


BUS_URL = "https://ulasim.canakkale.bel.tr/rehber/hatlar-otobus-saatleri/"
BUS_HOST = "ulasim.canakkale.bel.tr"
TURKEY_TZ = timezone(timedelta(hours=3))
BUS_CACHE_TTL = timedelta(hours=6)
DOWNLOAD_DIR = Path(__file__).resolve().parents[2] / "data" / "bus_schedules"
MANIFEST_MAX_AGE = timedelta(hours=8)


class BusService:
    def __init__(self):
        self._data: Optional[Dict] = None
        self._expires: Optional[datetime] = None
        self._refresh_lock = asyncio.Lock()

    def _cache_is_fresh(self) -> bool:
        return bool(self._data and self._expires and datetime.now() < self._expires)

    @staticmethod
    def _valid_source_url(url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme == "https" and parsed.hostname == BUS_HOST and parsed.path.lower().endswith(".pdf")

    def _get_refreshed_downloads(self) -> Optional[Dict]:
        """Read the most recent six-hour GitHub refresh when the source is unavailable."""
        try:
            manifest = json.loads((DOWNLOAD_DIR / "metadata.json").read_text(encoding="utf-8"))
            fetched_at = datetime.fromisoformat(manifest["fetched_at"])
            if fetched_at.tzinfo is None:
                fetched_at = fetched_at.replace(tzinfo=timezone.utc)
            age = datetime.now(timezone.utc) - fetched_at.astimezone(timezone.utc)
            if age < timedelta(0) or age > MANIFEST_MAX_AGE:
                return None

            pdfs = []
            for entry in manifest.get("pdfs", []):
                url = entry.get("url", "")
                filename = entry.get("filename", "")
                if (self._valid_source_url(url) and filename and Path(filename).name == filename
                        and (DOWNLOAD_DIR / filename).is_file()):
                    pdfs.append({"url": url, "label": entry.get("label") or filename})
            if not pdfs:
                return None
            return {
                "pdfs": pdfs,
                "last_update": fetched_at.astimezone(TURKEY_TZ).isoformat(),
                "source": "Çanakkale Belediyesi",
            }
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            return None

    def get_downloaded_pdf(self, url: str) -> Optional[bytes]:
        """Return a recently refreshed official PDF from the six-hour download set."""
        schedule = self._get_refreshed_downloads()
        if not schedule:
            return None
        try:
            manifest = json.loads((DOWNLOAD_DIR / "metadata.json").read_text(encoding="utf-8"))
            for entry in manifest.get("pdfs", []):
                if entry.get("url") != url:
                    continue
                filename = entry.get("filename", "")
                if not filename or Path(filename).name != filename:
                    return None
                content = (DOWNLOAD_DIR / filename).read_bytes()
                return content if content.startswith(b"%PDF-") else None
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return None
        return None

    def _parse_schedule(self, html: str) -> Dict:
        soup = BeautifulSoup(html, "html.parser")
        pdfs = []
        seen_urls = set()
        for link in soup.find_all("a", href=True):
            url = urljoin(BUS_URL, link["href"])
            if not self._valid_source_url(url):
                continue
            if url in seen_urls:
                continue
            seen_urls.add(url)
            label = " ".join(link.get_text(" ", strip=True).split())
            if not label:
                label = url.rsplit("/", 1)[-1].replace("-", " ").rsplit(".", 1)[0]
            pdfs.append({"url": url, "label": label})

        now = datetime.now(TURKEY_TZ)
        if not pdfs:
            raise ValueError("Resmi sayfada PDF bağlantısı bulunamadı")
        return {"pdfs": pdfs, "last_update": now.isoformat(), "source": "Çanakkale Belediyesi"}

    async def get_bus_schedule(self) -> Dict:
        if self._cache_is_fresh():
            return self._data
        async with self._refresh_lock:
            if self._cache_is_fresh():
                return self._data
            downloaded = self._get_refreshed_downloads()
            if downloaded:
                self._data = downloaded
                self._expires = datetime.now() + BUS_CACHE_TTL
                return downloaded
            try:
                timeout = httpx.Timeout(connect=3.0, read=6.0, write=3.0, pool=3.0)
                async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
                    response = await client.get(BUS_URL, headers={"User-Agent": "18MartPortal/1.0 (bus schedule reader)"})
                    response.raise_for_status()
                    final_host = urlparse(str(response.url)).hostname
                    if final_host != BUS_HOST:
                        raise ValueError("Belediye sayfası beklenmeyen bir adrese yönlendirildi")
                    result = self._parse_schedule(response.text)
                self._data = result
                self._expires = datetime.now() + BUS_CACHE_TTL
                return result
            except (httpx.HTTPError, ValueError) as exc:
                # Keep the last known official links available during a temporary source outage.
                if self._data:
                    return self._data
                downloaded = self._get_refreshed_downloads()
                if downloaded:
                    self._data = downloaded
                    self._expires = datetime.now() + BUS_CACHE_TTL
                    return downloaded
                raise RuntimeError(f"Otobüs saatleri resmi kaynaktan alınamadı: {exc}") from exc


bus_service = BusService()
