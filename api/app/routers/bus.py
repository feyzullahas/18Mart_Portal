import asyncio
from fastapi import APIRouter, HTTPException, Response, Query
import httpx
from app.services.bus_service import bus_service
from datetime import datetime, timedelta
from urllib.parse import urlparse

router = APIRouter(prefix="/bus", tags=["bus"])

# PDF bytes in-memory cache — URL bazli
_pdf_cache: dict = {}  # { "url": {"content": bytes, "expires": datetime} }

PDF_CACHE_TTL = timedelta(hours=6)
PDF_CACHE_CONTROL = "public, max-age=21600, s-maxage=21600, stale-while-revalidate=21600"
SCHEDULE_CACHE_CONTROL = "public, max-age=21600, s-maxage=21600, stale-while-revalidate=21600"


@router.get("/schedule")
async def get_bus_schedule(response: Response):
    """Otobüs saatleri PDF linklerini getirir"""
    response.headers["Cache-Control"] = SCHEDULE_CACHE_CONTROL
    try:
        return await bus_service.get_bus_schedule()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/pdf")
async def proxy_bus_pdf(url: str = Query(..., min_length=8)):
    """Otobus PDF'ini proxy'leyerek dondurur (CORS bypass + cache)"""
    pdf_url = url
    parsed = urlparse(pdf_url)
    if parsed.scheme != "https" or parsed.hostname != "ulasim.canakkale.bel.tr" or not parsed.path.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Yalnızca belediyenin resmi PDF bağlantıları kullanılabilir")

    # Prefer the recent six-hour download set; this keeps page loads independent
    # of slow responses from the municipality's file host.
    downloaded = bus_service.get_downloaded_pdf(pdf_url)
    if downloaded:
        return Response(
            content=downloaded,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline; filename=bus.pdf",
                "Cache-Control": PDF_CACHE_CONTROL,
                "X-Cache": "SCHEDULED-DISK",
            },
        )

    # Cache hit?
    cached = _pdf_cache.get(pdf_url)
    if cached and datetime.now() < cached["expires"]:
        return Response(
            content=cached["content"],
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline; filename=bus.pdf",
                "Cache-Control": PDF_CACHE_CONTROL,
                "X-Cache": "HIT",
            },
        )

    # Cache miss — belediye sitesinden cek
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://ulasim.canakkale.bel.tr/",
        }
        timeout = httpx.Timeout(connect=3.0, read=8.0, write=3.0, pool=3.0)
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            async with asyncio.timeout(12):
                async with client.stream("GET", pdf_url, headers=headers) as response:
                    if response.status_code != 200:
                        raise HTTPException(status_code=502, detail="PDF alinamadi")
                    content_type = response.headers.get("content-type", "").lower()
                    if response.url.host != "ulasim.canakkale.bel.tr" or "application/pdf" not in content_type:
                        raise HTTPException(status_code=502, detail="Resmi kaynak geçerli bir PDF döndürmedi")
                    chunks = []
                    size = 0
                    async for chunk in response.aiter_bytes():
                        size += len(chunk)
                        if size > 30 * 1024 * 1024:
                            raise HTTPException(status_code=502, detail="PDF dosyası beklenenden büyük")
                        chunks.append(chunk)
                    content = b"".join(chunks)
                    if not content.startswith(b"%PDF-"):
                        raise HTTPException(status_code=502, detail="Resmi kaynak geçerli bir PDF döndürmedi")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"PDF istegi basarisiz: {str(e)}")
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail="PDF resmi kaynaktan 12 saniye içinde alınamadı") from e
    except HTTPException:
        raise

    # Cache'e kaydet
    _pdf_cache[pdf_url] = {
        "content": content,
        "expires": datetime.now() + PDF_CACHE_TTL,
    }

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline; filename=bus.pdf",
            "Cache-Control": PDF_CACHE_CONTROL,
            "X-Cache": "MISS",
        },
    )
