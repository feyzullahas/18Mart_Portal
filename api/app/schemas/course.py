from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Ders oluştururken gelen veri
class CourseCreate(BaseModel):
    name: str
    code: Optional[str] = ""
    day: str  # Monday, Tuesday, etc.
    start_time: str  # 09:00 format
    end_time: str    # 11:00 format
    location: Optional[str] = ""
    instructor: Optional[str] = ""

# Ders güncelleme verisi
class CourseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    day: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    instructor: Optional[str] = None

# API'den dönen veri
class CourseResponse(BaseModel):
    id: int
    user_id: int
    name: str
    code: Optional[str]
    day: str
    start_time: str
    end_time: str
    location: Optional[str]
    instructor: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
