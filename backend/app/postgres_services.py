"""
PostgreSQL services for user authentication and course schedule CRUD operations.
Isolated from existing services.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

from .postgres_models import User, CourseSchedule
from .postgres_schemas import UserCreate, UserLogin, CourseScheduleCreate, CourseScheduleUpdate

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# User services
def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, user_login: UserLogin) -> Optional[User]:
    """Authenticate user credentials"""
    user = get_user_by_email(db, user_login.email)
    if not user:
        return None
    if not verify_password(user_login.password, user.password_hash):
        return None
    return user


# Course schedule services
def create_course_schedule(db: Session, schedule: CourseScheduleCreate, user_id: str) -> CourseSchedule:
    """Create a new course schedule for a user"""
    db_schedule = CourseSchedule(
        user_id=user_id,
        course_name=schedule.course_name,
        day_of_week=schedule.day_of_week,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
        location=schedule.location
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def get_user_course_schedules(db: Session, user_id: str) -> List[CourseSchedule]:
    """Get all course schedules for a user"""
    return db.query(CourseSchedule).filter(CourseSchedule.user_id == user_id).all()


def get_course_schedule_by_id(db: Session, schedule_id: str, user_id: str) -> Optional[CourseSchedule]:
    """Get a specific course schedule by ID for a user"""
    return db.query(CourseSchedule).filter(
        CourseSchedule.id == schedule_id,
        CourseSchedule.user_id == user_id
    ).first()


def update_course_schedule(
    db: Session, 
    schedule_id: str, 
    user_id: str, 
    schedule_update: CourseScheduleUpdate
) -> Optional[CourseSchedule]:
    """Update a course schedule"""
    db_schedule = get_course_schedule_by_id(db, schedule_id, user_id)
    if not db_schedule:
        return None
    
    update_data = schedule_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_schedule, field, value)
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def delete_course_schedule(db: Session, schedule_id: str, user_id: str) -> bool:
    """Delete a course schedule"""
    db_schedule = get_course_schedule_by_id(db, schedule_id, user_id)
    if not db_schedule:
        return False
    
    db.delete(db_schedule)
    db.commit()
    return True


def get_user_schedules_by_day(db: Session, user_id: str, day_of_week: str) -> List[CourseSchedule]:
    """Get user's course schedules for a specific day"""
    return db.query(CourseSchedule).filter(
        CourseSchedule.user_id == user_id,
        CourseSchedule.day_of_week == day_of_week
    ).all()
