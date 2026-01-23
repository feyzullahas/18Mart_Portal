"""
PostgreSQL routers for user authentication and course schedule endpoints.
Isolated from existing routers.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError

from .postgres_db import get_postgres_db
from .postgres_models import User, CourseSchedule
from .postgres_schemas import (
    UserCreate, UserLogin, UserResponse, UserAuth, Token,
    CourseScheduleCreate, CourseScheduleUpdate, CourseScheduleResponse,
    UserWithSchedules
)
from .postgres_services import (
    create_user, authenticate_user, create_access_token,
    create_course_schedule, get_user_course_schedules,
    get_course_schedule_by_id, update_course_schedule, delete_course_schedule,
    get_user_schedules_by_day
)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
schedule_router = APIRouter(prefix="/api/v1/schedules", tags=["course-schedules"])
security = HTTPBearer()


# Authentication endpoints
@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_postgres_db)):
    """Register a new user"""
    # Check if user already exists
    from .postgres_services import get_user_by_email
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = create_user(db, user)
    return db_user


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_postgres_db)):
    """Authenticate user and return access token"""
    user = authenticate_user(db, user_credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_postgres_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        from .postgres_services import SECRET_KEY, ALGORITHM
        from jose import jwt
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


# Course schedule endpoints
@schedule_router.post("/", response_model=CourseScheduleResponse)
async def create_schedule(
    schedule: CourseScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_postgres_db)
):
    """Create a new course schedule for the authenticated user"""
    return create_course_schedule(db, schedule, str(current_user.id))


@schedule_router.get("/", response_model=List[CourseScheduleResponse])
async def get_user_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_postgres_db),
    day_of_week: str = None
):
    """Get user's course schedules, optionally filtered by day"""
    if day_of_week:
        return get_user_schedules_by_day(db, str(current_user.id), day_of_week)
    return get_user_course_schedules(db, str(current_user.id))


@schedule_router.get("/{schedule_id}", response_model=CourseScheduleResponse)
async def get_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_postgres_db)
):
    """Get a specific course schedule"""
    schedule = get_course_schedule_by_id(db, schedule_id, str(current_user.id))
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    return schedule


@schedule_router.put("/{schedule_id}", response_model=CourseScheduleResponse)
async def update_schedule(
    schedule_id: str,
    schedule_update: CourseScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_postgres_db)
):
    """Update a course schedule"""
    schedule = update_course_schedule(db, schedule_id, str(current_user.id), schedule_update)
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    return schedule


@schedule_router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_postgres_db)
):
    """Delete a course schedule"""
    success = delete_course_schedule(db, schedule_id, str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    return {"message": "Schedule deleted successfully"}


@schedule_router.get("/user/with-schedules", response_model=UserWithSchedules)
async def get_user_with_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_postgres_db)
):
    """Get user info with all their course schedules"""
    schedules = get_user_course_schedules(db, str(current_user.id))
    return UserWithSchedules(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
        course_schedules=schedules
    )
