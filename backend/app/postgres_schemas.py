"""
Pydantic schemas for PostgreSQL user authentication and course schedules.
Isolated from existing schemas.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, time
from uuid import UUID


# User schemas
class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserAuth(BaseModel):
    """Schema for authenticated user"""
    id: UUID
    email: str

    class Config:
        from_attributes = True


# Course Schedule schemas
class CourseScheduleCreate(BaseModel):
    """Schema for creating a course schedule"""
    course_name: str
    day_of_week: str
    start_time: time
    end_time: time
    location: Optional[str] = None


class CourseScheduleUpdate(BaseModel):
    """Schema for updating a course schedule"""
    course_name: Optional[str] = None
    day_of_week: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = None


class CourseScheduleResponse(BaseModel):
    """Schema for course schedule response"""
    id: UUID
    user_id: UUID
    course_name: str
    day_of_week: str
    start_time: time
    end_time: time
    location: Optional[str]

    class Config:
        from_attributes = True


# Auth response schemas
class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token data"""
    user_id: Optional[UUID] = None


# Combined schemas
class UserWithSchedules(UserResponse):
    """Schema for user with their course schedules"""
    course_schedules: List[CourseScheduleResponse] = []
