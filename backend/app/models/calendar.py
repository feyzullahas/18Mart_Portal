from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from enum import Enum

class EventType(str, Enum):
    KAYIT = "kayit"
    SINAV = "sinav"
    DERS = "ders"
    TATIL = "tatil"
    ONEMLI = "onemli"

class Semester(str, Enum):
    GUZ = "guz"
    BAHAR = "bahar"
    YAZ = "yaz"

class CalendarEvent(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    event_type: EventType
    semester: Semester
    is_important: bool = False
