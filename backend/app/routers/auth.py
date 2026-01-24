from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from config.mysql import get_mysql_connection
from app.utils.security import hash_password, verify_password
import mysql.connector
from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    conn = get_mysql_connection()
    if not conn:
        raise HTTPException(
            status_code=500,
            detail="Veritabanı bağlantı hatası"
        )
    
    cursor = conn.cursor()

    try:
        # Email kontrolü
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (data.email,)
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Bu email zaten kayıtlı"
            )

        # Kullanıcı ekle
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
            (data.email, hash_password(data.password))
        )
        conn.commit()

        return {"message": "Kayıt başarılı"}

    except HTTPException as he:
        # Re-raise HTTPExceptions as-is
        conn.rollback()
        raise he
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail="Veritabanı hatası"
        )

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail="Sunucu hatası"
        )

    finally:
        cursor.close()
        conn.close()


@router.post("/login", response_model=Token)
def login(data: LoginRequest):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Kullanıcıyı email ile bul
        cursor.execute(
            "SELECT id, email, password_hash FROM users WHERE email = %s",
            (data.email,)
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Email veya şifre hatalı"
            )

        # Şifreyi kontrol et
        if not verify_password(data.password, user['password_hash']):
            raise HTTPException(
                status_code=401,
                detail="Email veya şifre hatalı"
            )

        # JWT token oluştur
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['email'], "user_id": str(user['id'])},
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except mysql.connector.Error as e:
        print("MYSQL ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Veritabanı hatası"
        )

    except Exception as e:
        print("GENEL ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Sunucu hatası"
        )

    finally:
        cursor.close()
        conn.close()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
