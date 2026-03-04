from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.course import Course
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from app.routers.auth_new import get_current_user
from typing import List

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("/", response_model=List[CourseResponse])
async def get_my_courses(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Kullanıcının kendi ders programını getirir"""
    
    courses = db.query(Course).filter(Course.user_id == current_user.id).all()
    return courses

@router.get("/all")
async def get_all_courses_grouped(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Haftanın tüm günleri için ders programını gruplandırılmış olarak getirir"""
    
    courses = db.query(Course).all()
    
    # Türkçe gün isimleri
    day_names_tr = {
        "Monday": "Pazartesi",
        "Tuesday": "Salı", 
        "Wednesday": "Çarşamba",
        "Thursday": "Perşembe",
        "Friday": "Cuma"
    }
    
    # Günlere göre grupla
    grouped_courses = {day: [] for day in day_names_tr.values()}
    
    for course in courses:
        day_tr = day_names_tr.get(course.day, course.day)
        if day_tr in grouped_courses:
            grouped_courses[day_tr].append({
                "name": course.name,
                "code": course.code,
                "start_time": course.start_time,
                "end_time": course.end_time,
                "location": course.location,
                "instructor": course.instructor
            })
    
    return grouped_courses

@router.post("/", response_model=CourseResponse)
async def add_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcı için yeni ders ekler"""
    
    new_course = Course(
        user_id=current_user.id,
        name=course_data.name,
        code=course_data.code,
        day=course_data.day,
        start_time=course_data.start_time,
        end_time=course_data.end_time,
        location=course_data.location,
        instructor=course_data.instructor
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return new_course

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ders bilgilerini günceller"""
    
    # Kullanıcının dersini bul
    course = db.query(Course).filter(
        Course.id == course_id, 
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Ders bulunamadı")
    
    # Güncellenecek alanları kontrol et
    update_data = course_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    
    return course

@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ders siler"""
    
    # Kullanıcının dersini bul
    course = db.query(Course).filter(
        Course.id == course_id, 
        Course.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Ders bulunamadı")
    
    db.delete(course)
    db.commit()
    
    return {"message": "Ders başarıyla silindi"}
