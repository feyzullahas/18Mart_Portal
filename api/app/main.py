from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os
from dotenv import load_dotenv

# .env dosyasını yükle ve environment variables ayarla
load_dotenv()
os.environ.setdefault('SECRET_KEY', '18mart_portal_super_secret_key_2024')
os.environ.setdefault('ALGORITHM', 'HS256')
os.environ.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', '30')

from app.routers import auth_new, courses_new, weather, calendar, meals, bus
from app.database import test_connection, create_tables

app = FastAPI(title="18Mart Portal API")

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
        "https://18-mart-portal-4orl.vercel.app",
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

handler = Mangum(app, lifespan="off")