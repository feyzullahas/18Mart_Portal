from fastapi import APIRouter
from app.services.bus_service import bus_service

router = APIRouter(prefix="/bus", tags=["bus"])

@router.get("/schedule")
async def get_bus_schedule():
    """Otobüs saatleri PDF linklerini getirir"""
    return await bus_service.get_bus_schedule()
