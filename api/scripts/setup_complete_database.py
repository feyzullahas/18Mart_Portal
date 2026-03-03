#!/usr/bin/env python3
"""
Complete PostgreSQL database setup script for 18Mart Portal.
This script creates all necessary tables and sets up the database structure.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.postgres_db import PostgresBase
from app.postgres_models import User, CourseSchedule, DailyMenu, OsemMenu, AcademicEvent, BusScheduleCache
from app.database import DATABASE_URL
import os
from dotenv import load_dotenv

load_dotenv()


def setup_database():
    """Set up the complete PostgreSQL database"""
    print("🚀 Starting PostgreSQL database setup...")
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable is not set!")
        print("Please set DATABASE_URL in your .env file")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        print("📊 Creating all tables...")
        
        # Create all tables
        PostgresBase.metadata.create_all(bind=engine)
        
        print("✅ All tables created successfully!")
        
        # Verify tables were created
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"📋 Created {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
        
        # Insert sample data if tables are empty
        with engine.connect() as connection:
            # Check if users table is empty
            user_count = connection.execute(text("SELECT COUNT(*) FROM users")).scalar()
            
            if user_count == 0:
                print("📝 Inserting sample academic events...")
                connection.execute(text("""
                    INSERT INTO academic_events (title, description, start_date, end_date, event_type, semester, academic_year, is_important) VALUES
                    ('2024-2025 Güz Dönemi Kayıtları', 'Güz dönemi ders kayıtlarının başlangıcı', '2024-09-16', '2024-09-20', 'kayit', 'guz', '2024-2025', true),
                    ('Ara Sınavlar', 'Güz dönemi ara sınavları', '2024-11-18', '2024-11-29', 'sinav', 'guz', '2024-2025', true),
                    ('Final Sınavları', 'Güz dönemi final sınavları', '2025-01-13', '2025-01-24', 'sinav', 'guz', '2024-2025', true),
                    ('Yarıyıl Tatili', 'Güz dönemi yarıyıl tatili', '2025-01-27', '2025-02-07', 'tatil', 'guz', '2024-2025', false)
                """))
                connection.commit()
                print("✅ Sample data inserted successfully!")
            else:
                print("ℹ️  Tables already contain data, skipping sample data insertion")
        
        print("\n🎉 Database setup completed successfully!")
        print("\n📖 Next steps:")
        print("1. Update your .env file with the correct DATABASE_URL")
        print("2. Run your FastAPI application")
        print("3. Test the API endpoints")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


def verify_connection():
    """Verify database connection before setup"""
    print("🔍 Verifying database connection...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL: {version}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🏛️  18Mart Portal - Complete PostgreSQL Database Setup")
    print("=" * 60)
    
    # Verify connection first
    if not verify_connection():
        print("\n❌ Please check your database connection and try again.")
        sys.exit(1)
    
    # Setup database
    if setup_database():
        print("\n✨ Setup completed successfully! Your database is ready to use.")
    else:
        print("\n💥 Setup failed. Please check the error messages above.")
        sys.exit(1)
