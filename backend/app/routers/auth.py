from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from config.mysql import get_mysql_connection
from app.utils.security import hash_password, verify_password
import mysql.connector
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class User:
    def __init__(self, id, email):
        self.id = id
        self.email = email

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        email: str = payload.get("sub")
        if user_id is None or email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    conn = get_mysql_connection()
    if not conn:
        raise credentials_exception
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, email FROM users WHERE id = %s AND email = %s",
            (user_id, email)
        )
        user_data = cursor.fetchone()
        
        if user_data is None:
            raise credentials_exception
            
        return User(id=user_data[0], email=user_data[1])
        
    finally:
        cursor.close()
        conn.close()


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

    except HTTPException as he:
        print("HTTP EXCEPTION:", he.detail)
        conn.rollback()
        raise he
    except mysql.connector.Error as e:
        print("MYSQL ERROR:", e)
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail="Veritabanı hatası"
        )

    except Exception as e:
        print("GENEL ERROR:", e)
        conn.rollback()
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
