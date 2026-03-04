from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler as rate_limit_handler
from slowapi.errors import RateLimitExceeded
from app.utils.limiter import limiter
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()
# SECRET_KEY mutlaka Vercel environment variables'dan gelmeli
# Buradaki fallback sadece lokal geliştirme içindir, production'da env var olmalı
os.environ.setdefault('ALGORITHM', 'HS256')
os.environ.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', '43200')

# SECRET_KEY kontrol — Vercel env var'da olmalı
if not os.getenv('SECRET_KEY'):
    import sys
    print("HATA: SECRET_KEY environment variable ayarlanmamış!", file=sys.stderr)

from app.routers import auth_new, courses_new, weather, calendar, meals, bus
from app.database import test_connection, create_tables

app = FastAPI(title="18Mart Portal API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Startup event - database tablolarını oluştur
@app.on_event("startup")
async def startup_event():
    print(" 18Mart Portal API başlatılıyor..")
    
    # Database bağlantısını test et
    if test_connection():
        print(" Database bağlantısı başarılı")
        # Tabloları oluştur (eğer yoksa)
        create_tables()
    else:
        print(" Database bağlantısı başarısız")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://18-mart-portal.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "http://localhost:5177",
        "http://127.0.0.1:5177",
        "http://localhost:5178",
        "http://127.0.0.1:5178",
        "http://localhost:5179",
        "http://127.0.0.1:5179",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(weather.router)
app.include_router(calendar.router)
app.include_router(meals.router)
app.include_router(bus.router)
# Yeni auth ve courses router'ları
app.include_router(auth_new.router)
app.include_router(courses_new.router)
# Eski router'ları yorum satırı yap
# app.include_router(auth.router)
# app.include_router(courses.router)


@app.get("/")
async def root():
    return {"message": "18Mart Portal API - Hoş Geldiniz!"}


@app.get("/health")
async def health():
    """Sistem durumunu diagnostik amaçlı kontrol et"""
    import os
    from sqlalchemy import text, inspect

    result = {
        "status": "checking",
        "secret_key_set": bool(os.getenv("SECRET_KEY")),
        "database_url_set": bool(os.getenv("DATABASE_URL")),
        "db_connection": False,
        "tables": [],
        "errors": []
    }

    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            result["db_connection"] = True

        inspector = inspect(engine)
        result["tables"] = inspector.get_table_names()

        # Tablolar yoksa oluşturmayı dene
        if "users" not in result["tables"]:
            from app.database import create_tables
            create_tables()
            result["tables"] = inspect(engine).get_table_names()
            result["errors"].append("users tablosu yoktu, oluşturuldu")

    except Exception as e:
        result["errors"].append(str(e))

    result["status"] = "ok" if result["db_connection"] else "error"
    return result

