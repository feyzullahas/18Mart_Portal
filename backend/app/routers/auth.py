from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from config.mysql import get_mysql_connection
from app.utils.security import hash_password
import mysql.connector

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    conn = get_mysql_connection()
    cursor = conn.cursor()

    try:
        # 🔎 Aktif DB kontrol (debug – istersen sonra sil)
        cursor.execute("SELECT DATABASE();")
        print("AKTIF DATABASE:", cursor.fetchone())

        # 🔎 Email kontrolü
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (data.email,)
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Bu email zaten kayıtlı"
            )

        # ➕ Kullanıcı ekle
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
            (data.email, hash_password(data.password))
        )
        conn.commit()

        return {"message": "Kayıt başarılı"}

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
