from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Database URL'i al (MySQL için)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+mysqlconnector://root:database9876@localhost/portal_db"
)

# Engine oluştur (database ile konuşan motor)
engine = create_engine(DATABASE_URL)

# Session oluşturucu
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tüm modellerin miras alacağı base class
Base = declarative_base()

# Her API isteği için database session'ı ver
def get_db():
    db = SessionLocal()
    try:
        yield db  # API'ye ver
    finally:
        db.close()  # İş bitince kapat

# Database tablolarını oluştur
def create_tables():
    """Tüm tabloları oluştur"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tabloları başarıyla oluşturuldu")

# Database bağlantısını test et
def test_connection():
    """Database bağlantısını test et"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database bağlantısı başarılı")
            return True
    except Exception as e:
        print(f"❌ Database bağlantı hatası: {e}")
        return False
