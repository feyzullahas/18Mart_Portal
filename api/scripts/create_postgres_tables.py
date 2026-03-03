"""
Script to create PostgreSQL tables for user authentication and course schedules.
This is isolated from existing database tables.
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.postgres_db import create_postgres_tables
from app.postgres_models import User, CourseSchedule

def main():
    """Create PostgreSQL tables"""
    print("Creating PostgreSQL tables for user authentication and course schedules...")
    
    try:
        # Create tables
        create_postgres_tables()
        print("✅ PostgreSQL tables created successfully!")
        print("\nCreated tables:")
        print("- users (id, email, password_hash, created_at)")
        print("- course_schedules (id, user_id, course_name, day_of_week, start_time, end_time, location)")
        
    except Exception as e:
        print(f"❌ Error creating PostgreSQL tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
