#!/usr/bin/env python3
"""
Yeni database yapısını test et
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import test_connection, create_tables
from app.models.user import User
from app.models.course import Course
from sqlalchemy.orm import sessionmaker

def test_new_structure():
    print("🔍 Yeni database yapısını test ediyorum...")
    
    # 1. Database bağlantısı test
    print("\n1. Database bağlantısı test:")
    if test_connection():
        print("✅ Bağlantı başarılı")
    else:
        print("❌ Bağlantı başarısız")
        return
    
    # 2. Tabloları oluştur
    print("\n2. Tablolar oluşturuluyor:")
    create_tables()
    
    # 3. Model test
    print("\n3. Model test:")
    from app.database import engine, SessionLocal
    
    # Test kullanıcı oluştur
    db = SessionLocal()
    try:
        # Test user
        test_user = User(
            email="test@newstructure.com",
            password_hash="test_hash_123"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Test kullanıcı oluşturuldu: {test_user}")
        
        # Test course
        test_course = Course(
            user_id=test_user.id,
            name="Test Dersi",
            code="TEST101",
            day="Monday",
            start_time="09:00",
            end_time="11:00",
            location="Test Salonu",
            instructor="Test Öğretmen"
        )
        db.add(test_course)
        db.commit()
        db.refresh(test_course)
        print(f"✅ Test ders oluşturuldu: {test_course}")
        
        # Test query
        user_courses = db.query(Course).filter(Course.user_id == test_user.id).all()
        print(f"✅ Kullanıcının dersleri: {len(user_courses)} adet")
        
        # Temizle
        db.delete(test_course)
        db.delete(test_user)
        db.commit()
        print("✅ Test verileri temizlendi")
        
    except Exception as e:
        print(f"❌ Model test hatası: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n🎉 Tüm testler tamamlandı!")

if __name__ == "__main__":
    test_new_structure()
