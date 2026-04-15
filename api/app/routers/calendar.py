from datetime import date, datetime

from fastapi import APIRouter, Query, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.calendar_task import CalendarTask
from app.models.user import User
from app.routers.auth_new import get_current_user
from app.services.calendar_service import calendar_service

router = APIRouter(prefix="/calendar", tags=["calendar"])


class PersonalCalendarCreateRequest(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


def _format_tr_date(target: date) -> str:
    months = {
        1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
        7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
    }
    return f"{target.day} {months[target.month]}"

@router.get("/list")
async def get_calendar_list():
    """Kullanılabilir takvimlerin listesini döndürür"""
    return calendar_service.get_calendars()

@router.get("/")
async def get_calendar_events(id: str = Query("general", description="Takvim ID'si")):
    """Seçilen takvimin etkinliklerini döndürür"""
    return calendar_service.get_events(id)


@router.get("/my")
def get_my_calendar_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Giriş yapan kullanıcının kişisel takvim görevlerini döndürür."""
    tasks = (
        db.query(CalendarTask)
        .filter(CalendarTask.user_id == current_user.id)
        .order_by(CalendarTask.task_date.asc(), CalendarTask.id.asc())
        .all()
    )

    today = date.today()
    events = []
    for task in tasks:
        days_left = (task.task_date - today).days
        events.append({
            "id": task.id,
            "start": task.task_date.isoformat(),
            "end": task.task_date.isoformat(),
            "title": task.title,
            "description": task.description,
            "type": "personal",
            "start_formatted": _format_tr_date(task.task_date),
            "end_formatted": _format_tr_date(task.task_date),
            "days_left": days_left,
            "is_past": task.task_date < today,
            "is_active": task.task_date == today,
        })

    return {
        "id": "my_calendar",
        "name": "Benim Takvimim",
        "events": events,
    }


@router.post("/my", status_code=status.HTTP_201_CREATED)
def create_my_calendar_event(
    payload: PersonalCalendarCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Giriş yapan kullanıcı için kişisel takvim görevi ekler."""
    try:
        target_date = datetime.strptime(payload.date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz tarih formatı. YYYY-MM-DD bekleniyor.")

    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Görev başlığı boş olamaz.")

    task = CalendarTask(
        user_id=current_user.id,
        task_date=target_date,
        title=title,
        description=payload.description.strip() if payload.description else None,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "message": "Görev kaydedildi.",
        "id": task.id,
    }
