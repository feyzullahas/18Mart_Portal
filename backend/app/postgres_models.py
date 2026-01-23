"""
PostgreSQL models for user authentication, course schedules, meal menus, and academic calendar.
Complete database models for 18Mart Portal.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Time, Date, Boolean, Text, Integer, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, date
from enum import Enum

from .postgres_db import PostgresBase


class User(PostgresBase):
    """User model for authentication and profile stored in PostgreSQL"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    student_id = Column(String(20), unique=True)
    department = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    course_schedules = relationship("CourseSchedule", back_populates="user", cascade="all, delete-orphan")


class CourseSchedule(PostgresBase):
    """Course schedule model stored in PostgreSQL"""
    __tablename__ = "course_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_name = Column(String(255), nullable=False)
    course_code = Column(String(20))
    instructor = Column(String(100))
    day_of_week = Column(String(20), nullable=False)  # Monday, Tuesday, etc.
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    location = Column(String(255))
    semester = Column(String(20), default='guz')
    academic_year = Column(String(9))  # Format: 2024-2025
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship with user
    user = relationship("User", back_populates="course_schedules")

    # Add constraints
    __table_args__ = (
        CheckConstraint("day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')", name='check_day_of_week'),
    )


class DailyMenu(PostgresBase):
    """Daily meal menu for main cafeteria stored in PostgreSQL"""
    __tablename__ = "daily_menus"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_date = Column(Date, unique=True, nullable=False, index=True)
    breakfast_items = Column(ARRAY(Text))
    dinner_items = Column(ARRAY(Text))
    total_calories_breakfast = Column(Integer, default=0)
    total_calories_dinner = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class OsemMenu(PostgresBase):
    """Daily meal menu for OSEM cafeteria stored in PostgreSQL"""
    __tablename__ = "osem_menus"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_date = Column(Date, unique=True, nullable=False, index=True)
    menu_items = Column(ARRAY(Text))
    total_calories = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


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


class AcademicEvent(PostgresBase):
    """Academic calendar events stored in PostgreSQL"""
    __tablename__ = "academic_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date)
    event_type = Column(String(20), nullable=False)  # kayit, sinav, ders, tatil, onemli
    semester = Column(String(10), nullable=False)  # guz, bahar, yaz
    academic_year = Column(String(9))  # Format: 2024-2025
    is_important = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Add constraints
    __table_args__ = (
        CheckConstraint("event_type IN ('kayit', 'sinav', 'ders', 'tatil', 'onemli')", name='check_event_type'),
        CheckConstraint("semester IN ('guz', 'bahar', 'yaz')", name='check_semester'),
    )


class BusScheduleCache(PostgresBase):
    """Cache for bus schedule PDF links stored in PostgreSQL"""
    __tablename__ = "bus_schedules_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_type = Column(String(20), nullable=False, index=True)  # weekday, weekend
    pdf_url = Column(Text, nullable=False)
    label = Column(String(255))
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), server_default=func.now())

    # Add constraints
    __table_args__ = (
        CheckConstraint("schedule_type IN ('weekday', 'weekend')", name='check_schedule_type'),
    )
