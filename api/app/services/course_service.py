from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Optional
from datetime import time
from ..models.course import Course, Base

import os
from dotenv import load_dotenv
load_dotenv()

# Ana database URL'ini kullan
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./courses.db")

if DATABASE_URL.startswith("postgresql") or DATABASE_URL.startswith("postgres"):
    engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
elif DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class CourseService:
    def __init__(self):
        self.days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.day_names_tr = {
            "Monday": "Pazartesi",
            "Tuesday": "Salı",
            "Wednesday": "Çarşamba",
            "Thursday": "Perşembe",
            "Friday": "Cuma"
        }

    def get_db(self):
        return SessionLocal()

    def get_all_courses(self) -> Dict[str, List[Dict]]:
        """Haftanın tüm günleri için dersleri döndürür"""
        db = self.get_db()
        try:
            courses = db.query(Course).all()

            # Günlere göre grupla
            grouped_courses = {day: [] for day in self.days_order}

            for course in courses:
                if course.day in grouped_courses:
                    grouped_courses[course.day].append(course.to_dict())

            # Her gün için dersleri saate göre sırala
            for day in grouped_courses:
                grouped_courses[day].sort(key=lambda x: x["start_time"])

            # Türkçe gün isimleri ile döndür
            result = {}
            for day in self.days_order:
                result[self.day_names_tr[day]] = grouped_courses[day]

            return result
        finally:
            db.close()

    def get_courses_by_day(self, day: str) -> List[Dict]:
        """Belirli bir gün için dersleri döndürür"""
        db = self.get_db()
        try:
            courses = db.query(Course).filter(Course.day == day).order_by(Course.start_time).all()
            return [course.to_dict() for course in courses]
        finally:
            db.close()

    def add_course(self, course_data: Dict) -> Dict:
        """Yeni ders ekler"""
        db = self.get_db()
        try:
            # Zaman formatını kontrol et ve dönüştür
            start_time = time.fromisoformat(course_data["start_time"]) if isinstance(course_data["start_time"], str) else course_data["start_time"]
            end_time = time.fromisoformat(course_data["end_time"]) if isinstance(course_data["end_time"], str) else course_data["end_time"]

            course = Course(
                name=course_data["name"],
                code=course_data["code"],
                day=course_data["day"],
                start_time=start_time,
                end_time=end_time,
                location=course_data.get("location", ""),
                instructor=course_data.get("instructor", "")
            )

            db.add(course)
            db.commit()
            db.refresh(course)

            return course.to_dict()
        finally:
            db.close()

    def update_course(self, course_id: int, course_data: Dict) -> Optional[Dict]:
        """Ders bilgilerini günceller"""
        db = self.get_db()
        try:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                return None

            # Zaman formatını kontrol et ve dönüştür
            if "start_time" in course_data:
                course.start_time = time.fromisoformat(course_data["start_time"]) if isinstance(course_data["start_time"], str) else course_data["start_time"]
            if "end_time" in course_data:
                course.end_time = time.fromisoformat(course_data["end_time"]) if isinstance(course_data["end_time"], str) else course_data["end_time"]

            # Diğer alanları güncelle
            for key, value in course_data.items():
                if key not in ["start_time", "end_time"] and hasattr(course, key):
                    setattr(course, key, value)

            db.commit()
            db.refresh(course)

            return course.to_dict()
        finally:
            db.close()

    def delete_course(self, course_id: int) -> bool:
        """Ders siler"""
        db = self.get_db()
        try:
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                return False

            db.delete(course)
            db.commit()
            return True
        finally:
            db.close()

course_service = CourseService()