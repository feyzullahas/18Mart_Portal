from fastapi import APIRouter, Query
from app.services.calendar_service import calendar_service

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/list")
async def get_calendar_list():
    """Kullanılabilir takvimlerin listesini döndürür"""
    return calendar_service.get_calendars()

@router.get("/")
async def get_calendar_events(id: str = Query("general", description="Takvim ID'si")):
    """Seçilen takvimin etkinliklerini döndürür"""
    return calendar_service.get_events(id)
