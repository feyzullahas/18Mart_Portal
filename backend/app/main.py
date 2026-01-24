from app.routers import test_mysql
from app.routers import auth
from app.routers import courses

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import weather, calendar, meals, bus, mysql_test
from app.routers.mysql_test import router as mysql_test_router

app = FastAPI(title="18Mart Portal API")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(test_mysql.router)
app.include_router(mysql_test_router)
app.include_router(weather.router)
app.include_router(calendar.router)
app.include_router(meals.router)
app.include_router(bus.router)
app.include_router(auth.router)
app.include_router(courses.router)


@app.get("/")
async def root():
    return {"message": "18Mart Portal API - Hoş Geldiniz!"}