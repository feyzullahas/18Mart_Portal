from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

VALID_DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}

# Ders oluştururken gelen veri
class CourseCreate(BaseModel):
    name: str
    code: Optional[str] = ""
    day: str
    start_time: str
    end_time: str
    location: Optional[str] = ""
    instructor: Optional[str] = ""

    @field_validator('name')
    @classmethod
    def name_length(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 1:
            raise ValueError('Ders adı boş olamaz')
        if len(v) > 100:
            raise ValueError('Ders adı en fazla 100 karakter olabilir')
        return v

    @field_validator('code')
    @classmethod
    def code_length(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 20:
            raise ValueError('Ders kodu en fazla 20 karakter olabilir')
        return v

    @field_validator('day')
    @classmethod
    def day_valid(cls, v: str) -> str:
        if v not in VALID_DAYS:
            raise ValueError(f'Geçerli günler: {", ".join(sorted(VALID_DAYS))}')
        return v

    @field_validator('start_time', 'end_time')
    @classmethod
    def time_format(cls, v: str) -> str:
        import re
        if not re.match(r'^\d{2}:\d{2}$', v):
            raise ValueError('Saat formatı HH:MM olmalıdır (örn: 09:00)')
        return v

    @field_validator('location')
    @classmethod
    def location_length(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 200:
            raise ValueError('Konum en fazla 200 karakter olabilir')
        return v

    @field_validator('instructor')
    @classmethod
    def instructor_length(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 100:
            raise ValueError('Öğretim görevlisi adı en fazla 100 karakter olabilir')
        return v

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
