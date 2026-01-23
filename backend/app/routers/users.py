from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models.user import User
from ..models.schedule import Schedule
from ..schemas.user import UserCreate, UserResponse, UserUpdate
from ..schemas.schedule import ScheduleCreate, ScheduleResponse
from ..auth import get_current_active_user, get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # Kullanıcı adı veya email zaten var mı kontrol et
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email) | (User.student_id == user.student_id)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username, email or student ID already registered"
        )
    
    # Yeni kullanıcı oluştur
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        student_id=user.student_id,
        department=user.department,
        password_hash=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    update_data = user_update.dict(exclude_unset=True)
    
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/{user_id}/schedules", response_model=List[ScheduleResponse])
async def get_user_schedules(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Sadece kendi programını görebilsin
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's schedules"
        )
    
    schedules = db.query(Schedule).filter(Schedule.user_id == user_id).all()
    return schedules
