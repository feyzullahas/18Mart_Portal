from fastapi import APIRouter
from app.services.meal_service import meal_service

router = APIRouter(prefix="/meals", tags=["meals"])

@router.get("/osem")
async def get_osem():
    """ÖSEM yemek listesini getirir"""
    return await meal_service.get_osem_meals()

@router.get("/kyk")
async def get_kyk():
    """KYK yemek listesini getirir"""
    return await meal_service.get_kyk_meals()
