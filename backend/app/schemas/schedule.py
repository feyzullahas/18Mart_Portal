from pydantic import BaseModel
from typing import Optional
from datetime import datetime, time
from uuid import UUID

class ScheduleBase(BaseModel):
    course_name: str
    day_of_week: str
    start_time: time
    end_time: time
    location: str

class ScheduleCreate(ScheduleBase):
    user_id: UUID

class ScheduleUpdate(BaseModel):
    course_name: Optional[str] = None
    day_of_week: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = None

class ScheduleResponse(ScheduleBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
