from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

# Kullanıcı oluştururken gelen veri
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Şifre en az 6 karakter olmalıdır')
        if len(v) > 128:
            raise ValueError('Şifre en fazla 128 karakter olabilir')
        if not any(c.isdigit() for c in v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        return v

# Kullanıcı giriş verisi
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# API'den dönen veri (şifre YOK!)
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Token response
class Token(BaseModel):
    access_token: str
    token_type: str

# Token data (JWT payload)
class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None
    full_name: Optional[str] = None
