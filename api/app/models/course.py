from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class Course(Base):
    __tablename__ = "courses"  # Tablo adı
    
    # Sütunlar
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=True)
    day = Column(String(20), nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(String(10), nullable=False)  # 09:00 format
    end_time = Column(String(10), nullable=False)    # 11:00 format
    location = Column(String(200), nullable=True)
    instructor = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # İlişkiler
    user = relationship("User", backref="courses")
    
    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}', day='{self.day}')>"
    
    def to_dict(self):
        """Course objesini dictionary'e çevir"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "code": self.code,
            "day": self.day,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "location": self.location,
            "instructor": self.instructor,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
