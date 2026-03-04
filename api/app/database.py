from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Database URL'i al (PostgreSQL/Neon için)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./portal_db.db"  # Lokal geliştirme için fallback
)

# Neon ve bazı sağlayıcılar 'postgres://' verir, SQLAlchemy 'postgresql://' ister
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# psycopg2 'channel_binding' parametresini tanımıyor, URL'den temizle
if "channel_binding" in DATABASE_URL:
    import re
    DATABASE_URL = re.sub(r'[&?]channel_binding=[^&]*', '', DATABASE_URL)
    DATABASE_URL = re.sub(r'\?&', '?', DATABASE_URL)  # ?& → ?
    DATABASE_URL = DATABASE_URL.rstrip('?').rstrip('&')

# PostgreSQL ise SSL ayarı ekle (URL'de sslmode yoksa)
if DATABASE_URL.startswith("postgresql"):
    if "sslmode" not in DATABASE_URL:
        engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
    else:
        engine = create_engine(DATABASE_URL)
else:
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
    # Modelleri import et ki Base onları tanısın
    from app.models import user, course  # noqa
    Base.metadata.create_all(bind=engine)
    print("✅ Database tabloları başarıyla oluşturuldu")

# Uygulama başladığında tabloları otomatik oluştur (serverless için)
# Sadece PostgreSQL bağlantısı varsa çalıştır, yoksa startup event halleder
try:
    if DATABASE_URL != "sqlite:///./portal_db.db":
        from app.models import user, course  # noqa
        Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"⚠️ Tablo oluşturma hatası (devam ediliyor): {e}")

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
