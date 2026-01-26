from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Kullanıcı oluştururken gelen veri
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Kullanıcı giriş verisi
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# API'den dönen veri (şifre YOK!)
class UserResponse(BaseModel):
    id: int
    email: str
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
