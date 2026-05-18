from fastapi import APIRouter, HTTPException, Response, Query
from fastapi.responses import Response
import httpx
from app.services.bus_service import bus_service
from datetime import datetime, timedelta

router = APIRouter(prefix="/bus", tags=["bus"])

# PDF bytes in-memory cache — URL bazli
_pdf_cache: dict = {}  # { "url": {"content": bytes, "expires": datetime} }

PDF_CACHE_TTL = timedelta(seconds=43200)
PDF_CACHE_CONTROL = "public, s-maxage=43200, stale-while-revalidate=43200"


@router.get("/schedule")
async def get_bus_schedule(response: Response):
    """Otobüs saatleri PDF linklerini getirir"""
    response.headers["Cache-Control"] = PDF_CACHE_CONTROL
    return await bus_service.get_bus_schedule()


@router.get("/pdf")
async def proxy_bus_pdf(url: str = Query(..., min_length=8)):
    """Otobus PDF'ini proxy'leyerek dondurur (CORS bypass + cache)"""
    pdf_url = url

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
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(pdf_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="PDF alinamadi")
            content = response.content
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"PDF istegi basarisiz: {str(e)}")

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
