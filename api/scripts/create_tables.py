#!/usr/bin/env python3
"""
Veritabanı tablolarını oluşturan script
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models import *

def create_tables():
    """Tüm modeller için veritabanı tablolarını oluştur"""
    print("Veritabanı tabloları oluşturuluyor...")
    Base.metadata.create_all(bind=engine)
    print("Tablolar başarıyla oluşturuldu!")

if __name__ == "__main__":
    create_tables()
