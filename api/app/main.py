from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
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

from app.routers import auth_new, courses_new, weather, calendar, meals, bus
from app.database import test_connection, create_tables

app = FastAPI(title="18Mart Portal API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

