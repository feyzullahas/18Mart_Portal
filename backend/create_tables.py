#!/usr/bin/env python3
"""
Database Migration Script for 18Mart Portal
Creates PostgreSQL tables with UUID support for users and schedules
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, create_tables
from app.models import user, schedule  # Import to register models

def main():
    """Create database tables"""
    print("Creating database tables...")
    
    try:
        # Create all tables
        create_tables()
        print("✅ Database tables created successfully!")
        
        # Print table information
        print("\n📋 Created tables:")
        print("- users (with UUID primary key)")
        print("- schedules (with UUID foreign key to users)")
        
        print("\n🔧 Database schema is ready for use!")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
