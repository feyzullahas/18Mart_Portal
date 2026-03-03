from fastapi import APIRouter, Query
from typing import Optional
from app.services.meal_service import meal_service

router = APIRouter(prefix="/meals", tags=["meals"])

@router.get("/osem")
async def get_osem():
    """ÖSEM yemek listesini getirir"""
    return await meal_service.get_osem_meals()

@router.get("/kyk")
async def get_kyk(
    year: Optional[int] = Query(None, description="Yıl (örn: 2026). Boş bırakılırsa mevcut yıl kullanılır."),
    month: Optional[int] = Query(None, ge=1, le=12, description="Ay (1-12). Boş bırakılırsa mevcut ay kullanılır.")
):
    """KYK yemek listesini getirir. year ve month parametreleri opsiyoneldir."""
    return await meal_service.get_kyk_meals(year=year, month=month)
