from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from sqlalchemy import inspect, text
import os
import re
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
    DATABASE_URL = re.sub(r'[&?]channel_binding=[^&]*', '', DATABASE_URL)
    DATABASE_URL = re.sub(r'\?&', '?', DATABASE_URL)
    DATABASE_URL = DATABASE_URL.rstrip('?').rstrip('&')

# Engine oluştur
# NullPool: Vercel/Lambda gibi serverless ortamlarda zorunlu —
# connection pool tutulmaz, her istek kendi bağlantısını açar ve kapatır.
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,
        connect_args={"sslmode": "require"} if "sslmode" not in DATABASE_URL else {},
    )
else:
    engine = create_engine(DATABASE_URL, poolclass=NullPool)

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
    from app.models import user, course, calendar_task  # noqa
    Base.metadata.create_all(bind=engine)
    ensure_user_full_name_column()
    print("[OK] Database tablolari basariyla olusturuldu")


def ensure_user_full_name_column():
    """Mevcut users tablosunda full_name kolonu yoksa ekler."""
    try:
        inspector = inspect(engine)
        if "users" not in inspector.get_table_names():
            return

        columns = {column["name"] for column in inspector.get_columns("users")}
        if "full_name" in columns:
            return

        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(255)"))

        print("[OK] users.full_name kolonu eklendi")
    except Exception as e:
        print(f"[WARN] users.full_name kolon kontrolu hatasi: {e}")

# Uygulama başladığında tabloları otomatik oluştur (serverless için)
# Sadece PostgreSQL bağlantısı varsa çalıştır, yoksa startup event halleder
try:
    if DATABASE_URL != "sqlite:///./portal_db.db":
        from app.models import user, course, calendar_task  # noqa
        Base.metadata.create_all(bind=engine)
        ensure_user_full_name_column()
except Exception as e:
    print(f"[WARN] Tablo olusturma hatasi (devam ediliyor): {e}")
# Database bağlantısını test et
def test_connection():
    """Database bağlantısını test et"""
    try:
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("[OK] Database baglantisi basarili")
            return True
    except Exception as e:
        print(f"[ERR] Database baglanti hatasi: {e}")
        return False
