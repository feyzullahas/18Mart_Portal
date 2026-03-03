from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, List
from pydantic import BaseModel
from config.mysql import get_mysql_connection
from app.routers.auth import get_current_user
import mysql.connector
import json

router = APIRouter(prefix="/courses", tags=["courses"])

class CourseCreate(BaseModel):
    name: str
    code: str
    day: str
    start_time: str
    end_time: str
    location: str = ""
    instructor: str = ""

class CourseResponse(BaseModel):
    id: int
    user_id: int
    name: str
    code: str
    day: str
    start_time: str
    end_time: str
    location: str
    instructor: str
    created_at: str
    updated_at: str

@router.get("/", response_model=List[CourseResponse])
async def get_my_courses(current_user = Depends(get_current_user)):
    """Kullanıcının kendi ders programını getirir"""
    conn = get_mysql_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantı hatası")
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            """
            SELECT id, user_id, course_name, course_code, day_of_week, 
                   start_time, end_time, location, instructor, 
                   created_at, updated_at
            FROM schedules 
            WHERE user_id = %s 
            ORDER BY day_of_week, start_time
            """,
            (current_user.id,)
        )
        
        courses = cursor.fetchall()
        
        # Map database columns to response format
        result = []
        for course in courses:
            result.append({
                "id": course["id"],
                "user_id": course["user_id"],
                "name": course["course_name"],
                "code": course["course_code"],
                "day": course["day_of_week"],
                "start_time": str(course["start_time"]),
                "end_time": str(course["end_time"]),
                "location": course["location"],
                "instructor": course["instructor"],
                "created_at": str(course["created_at"]),
                "updated_at": str(course["updated_at"])
            })
        
        return result
        
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Dersler alınırken hata oluştu: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/all")
async def get_all_courses_grouped():
    """Haftanın tüm günleri için ders programını gruplandırılmış olarak getirir (genel görünüm)"""
    conn = get_mysql_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantı hatası")
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            """
            SELECT course_name, course_code, day_of_week, 
                   start_time, end_time, location, instructor
            FROM schedules 
            ORDER BY day_of_week, start_time
            """
        )
        
        courses = cursor.fetchall()
        
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
            day_tr = day_names_tr.get(course["day_of_week"], course["day_of_week"])
            if day_tr in grouped_courses:
                grouped_courses[day_tr].append({
                    "name": course["course_name"],
                    "code": course["course_code"],
                    "start_time": str(course["start_time"]),
                    "end_time": str(course["end_time"]),
                    "location": course["location"],
                    "instructor": course["instructor"]
                })
        
        return grouped_courses
        
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Ders programı alınırken hata oluştu: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.post("/", response_model=CourseResponse)
async def add_course(course_data: CourseCreate, current_user = Depends(get_current_user)):
    """Kullanıcı için yeni ders ekler"""
    conn = get_mysql_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantı hatası")
    
    cursor = conn.cursor()
    
    try:
        # Gün adının geçerli olup olmadığını kontrol et
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        if course_data.day not in valid_days:
            raise HTTPException(status_code=400, detail="Geçersiz gün adı")
        
        cursor.execute(
            """
            INSERT INTO schedules 
            (user_id, course_name, course_code, day_of_week, start_time, end_time, location, instructor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                current_user.id,
                course_data.name,
                course_data.code,
                course_data.day,
                course_data.start_time,
                course_data.end_time,
                course_data.location,
                course_data.instructor
            )
        )
        
        conn.commit()
        course_id = cursor.lastrowid
        
        # Eklenen dersi geri döndür
        cursor.execute(
            """
            SELECT id, user_id, course_name, course_code, day_of_week, 
                   start_time, end_time, location, instructor, 
                   created_at, updated_at
            FROM schedules 
            WHERE id = %s
            """,
            (course_id,)
        )
        
        course = cursor.fetchone()
        
        return {
            "id": course[0],
            "user_id": course[1],
            "name": course[2],
            "code": course[3],
            "day": course[4],
            "start_time": str(course[5]),
            "end_time": str(course[6]),
            "location": course[7],
            "instructor": course[8],
            "created_at": str(course[9]),
            "updated_at": str(course[10])
        }
        
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Ders eklenirken hata oluştu: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.put("/{course_id}")
async def update_course(course_id: int, course_data: Dict, current_user = Depends(get_current_user)):
    """Ders bilgilerini günceller"""
    conn = get_mysql_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantı hatası")
    
    cursor = conn.cursor()
    
    try:
        # Önce dersin var olup olmadığını ve kullanıcının kendi dersi olduğunu kontrol et
        cursor.execute(
            "SELECT id FROM schedules WHERE id = %s AND user_id = %s",
            (course_id, current_user.id)
        )
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Ders bulunamadı veya yetkiniz yok")
        
        # Güncelleme sorgusu oluştur
        update_fields = []
        update_values = []
        
        if "name" in course_data:
            update_fields.append("course_name = %s")
            update_values.append(course_data["name"])
        
        if "code" in course_data:
            update_fields.append("course_code = %s")
            update_values.append(course_data["code"])
        
        if "day" in course_data:
            valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            if course_data["day"] not in valid_days:
                raise HTTPException(status_code=400, detail="Geçersiz gün adı")
            update_fields.append("day_of_week = %s")
            update_values.append(course_data["day"])
        
        if "start_time" in course_data:
            update_fields.append("start_time = %s")
            update_values.append(course_data["start_time"])
        
        if "end_time" in course_data:
            update_fields.append("end_time = %s")
            update_values.append(course_data["end_time"])
        
        if "location" in course_data:
            update_fields.append("location = %s")
            update_values.append(course_data["location"])
        
        if "instructor" in course_data:
            update_fields.append("instructor = %s")
            update_values.append(course_data["instructor"])
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="Güncellenecek alan bulunamadı")
        
        update_values.extend([course_id, current_user.id])
        
        cursor.execute(
            f"""
            UPDATE schedules 
            SET {', '.join(update_fields)}
            WHERE id = %s AND user_id = %s
            """,
            update_values
        )
        
        conn.commit()
        
        return {"message": "Ders başarıyla güncellendi"}
        
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Ders güncellenirken hata oluştu: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.delete("/{course_id}")
async def delete_course(course_id: int, current_user = Depends(get_current_user)):
    """Ders siler"""
    conn = get_mysql_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Veritabanı bağlantı hatası")
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM schedules WHERE id = %s AND user_id = %s",
            (course_id, current_user.id)
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ders bulunamadı veya yetkiniz yok")
        
        conn.commit()
        
        return {"message": "Ders başarıyla silindi"}
        
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Ders silinirken hata oluştu: {str(e)}")
    finally:
        cursor.close()
        conn.close()