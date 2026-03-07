from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx
from app.services.bus_service import bus_service

router = APIRouter(prefix="/bus", tags=["bus"])

@router.get("/schedule")
async def get_bus_schedule():
    """Otobüs saatleri PDF linklerini getirir"""
    return await bus_service.get_bus_schedule()

@router.get("/pdf/{schedule_type}")
async def proxy_bus_pdf(schedule_type: str):
    """Otobüs saatleri PDF'ini proxy'leyerek döndürür (CORS bypass)"""
    if schedule_type not in ("weekday", "weekend"):
        raise HTTPException(status_code=400, detail="Geçersiz tür. 'weekday' veya 'weekend' olmalı.")

    schedule = await bus_service.get_bus_schedule()

    entry = schedule.get(schedule_type)
    if not entry or not entry.get("url"):
        raise HTTPException(status_code=404, detail="PDF bulunamadı")

    pdf_url = entry["url"]

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://ulasim.canakkale.bel.tr/",
        }
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(pdf_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="PDF alınamadı")
            content = response.content

        return StreamingResponse(
            iter([content]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={schedule_type}.pdf",
                "Cache-Control": "public, max-age=3600",
            },
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"PDF isteği başarısız: {str(e)}")
