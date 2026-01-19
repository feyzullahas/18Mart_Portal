from fastapi import APIRouter, HTTPException
from typing import Dict, List
from ..services.course_service import course_service

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("/")
async def get_all_courses() -> Dict[str, List[Dict]]:
    """Haftanın tüm günleri için ders programını getirir"""
    try:
        return course_service.get_all_courses()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ders programı alınırken hata oluştu: {str(e)}")

@router.get("/{day}")
async def get_courses_by_day(day: str) -> List[Dict]:
    """Belirli bir gün için dersleri getirir"""
    try:
        return course_service.get_courses_by_day(day)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dersler alınırken hata oluştu: {str(e)}")

@router.post("/")
async def add_course(course_data: Dict):
    """Yeni ders ekler"""
    try:
        required_fields = ["name", "code", "day", "start_time", "end_time"]
        for field in required_fields:
            if field not in course_data:
                raise HTTPException(status_code=400, detail=f"Zorunlu alan eksik: {field}")

        # Gün adının geçerli olup olmadığını kontrol et
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        if course_data["day"] not in valid_days:
            raise HTTPException(status_code=400, detail="Geçersiz gün adı")

        return course_service.add_course(course_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ders eklenirken hata oluştu: {str(e)}")

@router.put("/{course_id}")
async def update_course(course_id: int, course_data: Dict):
    """Ders bilgilerini günceller"""
    try:
        updated_course = course_service.update_course(course_id, course_data)
        if not updated_course:
            raise HTTPException(status_code=404, detail="Ders bulunamadı")

        return updated_course
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ders güncellenirken hata oluştu: {str(e)}")

@router.delete("/{course_id}")
async def delete_course(course_id: int):
    """Ders siler"""
    try:
        success = course_service.delete_course(course_id)
        if not success:
            raise HTTPException(status_code=404, detail="Ders bulunamadı")

        return {"message": "Ders başarıyla silindi"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ders silinirken hata oluştu: {str(e)}")