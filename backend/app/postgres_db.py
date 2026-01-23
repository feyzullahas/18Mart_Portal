"""
Isolated PostgreSQL database connection for user authentication and course schedules.
This is completely separate from the existing database integration.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection URL for user authentication and schedules
POSTGRES_URL = os.getenv(
    "POSTGRES_URL", 
    "postgresql://username:password@localhost/mart_portal_auth"
)

# SQLAlchemy engine for PostgreSQL
postgres_engine = create_engine(
    POSTGRES_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

# Session factory for PostgreSQL
PostgresSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)

# Base model for PostgreSQL tables
PostgresBase = declarative_base()

# Dependency to get PostgreSQL database session
def get_postgres_db():
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create PostgreSQL tables
def create_postgres_tables():
    PostgresBase.metadata.create_all(bind=postgres_engine)
