#!/usr/bin/env python3
"""
Database migration - mevcut tabloları yeni yapıya göre güncelle
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

def migrate_database():
    print("🔄 Database migration başlatılıyor...")
    
    with engine.connect() as connection:
        # Users tablosunu güncelle
        print("\n1. Users tablosu güncelleniyor...")
        
        # is_active sütunu ekle (eğer yoksa)
        try:
            connection.execute(text("""
                ALTER TABLE users 
                ADD COLUMN is_active BOOLEAN DEFAULT TRUE
            """))
            print("✅ is_active sütunu eklendi")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("✅ is_active sütunu zaten mevcut")
            else:
                print(f"❌ is_active sütunu eklenemedi: {e}")
        
        # created_at sütunu ekle (eğer yoksa)
        try:
            connection.execute(text("""
                ALTER TABLE users 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """))
            print("✅ created_at sütunu eklendi")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("✅ created_at sütunu zaten mevcut")
            else:
                print(f"❌ created_at sütunu eklenemedi: {e}")
        
        # updated_at sütunu ekle (eğer yoksa)
        try:
            connection.execute(text("""
                ALTER TABLE users 
                ADD COLUMN updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP
            """))
            print("✅ updated_at sütunu eklendi")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("✅ updated_at sütunu zaten mevcut")
            else:
                print(f"❌ updated_at sütunu eklenemedi: {e}")
        
        # Courses tablosunu güncelle (varsa)
        print("\n2. Courses tablosu kontrol ediliyor...")
        
        # courses tablosunu oluştur (eğer yoksa)
        try:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    code VARCHAR(50),
                    day VARCHAR(20) NOT NULL,
                    start_time VARCHAR(10) NOT NULL,
                    end_time VARCHAR(10) NOT NULL,
                    location VARCHAR(200),
                    instructor VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    INDEX idx_user_id (user_id),
                    INDEX idx_day (day)
                )
            """))
            print("✅ Courses tablosu hazır")
        except Exception as e:
            print(f"❌ Courses tablosu hatası: {e}")
        
        # Eski schedules tablosundaki verileri courses tablosuna taşı
        try:
            result = connection.execute(text("SELECT COUNT(*) FROM schedules"))
            schedules_count = result.fetchone()[0]
            
            if schedules_count > 0:
                print(f"\n3. {schedules_count} adet schedules kaydı courses tablosuna taşınıyor...")
                
                connection.execute(text("""
                    INSERT IGNORE INTO courses (
                        user_id, name, code, day, start_time, end_time, 
                        location, instructor, created_at
                    )
                    SELECT 
                        user_id, 
                        course_name as name,
                        course_code as code,
                        day_of_week as day,
                        start_time,
                        end_time,
                        location,
                        instructor,
                        created_at
                    FROM schedules
                """))
                
                print("✅ Veriler taşındı")
            else:
                print("✅ Taşınacak veri bulunamadı")
                
        except Exception as e:
            print(f"❌ Veri taşıma hatası: {e}")
        
        connection.commit()
    
    print("\n🎉 Migration tamamlandı!")

if __name__ == "__main__":
    migrate_database()
