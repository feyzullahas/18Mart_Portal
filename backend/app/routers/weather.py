from fastapi import APIRouter, HTTPException
from app.services.weather_service import weather_service

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/current")
async def get_current_weather():
    """Güncel hava durumunu getirir"""
    data = await weather_service.get_current_weather()
    if not data:
        raise HTTPException(status_code=500, detail="Hava durumu alınamadı")
    return data

@router.get("/forecast")
async def get_forecast(days: int = 5):
    """Hava durumu tahminini getirir"""
    if days < 1 or days > 7:
        raise HTTPException(status_code=400, detail="Gün sayısı 1-7 arası olmalı")
    
    data = await weather_service.get_forecast(days)
    if not data:
        raise HTTPException(status_code=500, detail="Tahmin alınamadı")
    return data
