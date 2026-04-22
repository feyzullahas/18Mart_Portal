from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, TokenData
from app.utils.security import hash_password, verify_password
from app.utils.limiter import limiter
from datetime import datetime, timedelta
from jose import jwt, JWTError
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token as google_id_token
import os
import secrets

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
# 1 yıl — çıkış yapılmadıkça oturum kapanmaz
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "525600"))

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class GoogleLoginRequest(BaseModel):
    id_token: str

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
        token_data = TokenData(email=email, user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == int(user_id), User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Yeni kullanıcı kaydı"""
    
    # Email kontrolü
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Bu email zaten kayıtlı"
        )

    # Yeni kullanıcı oluştur
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """Kullanıcı girişi"""
    
    # Kullanıcıyı email ile bul
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Email veya şifre hatalı"
        )

    # JWT token oluştur
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/google", response_model=Token)
@limiter.limit("20/minute")
def login_with_google(request: Request, payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Google hesabı ile giriş yapar veya kullanıcıyı otomatik oluşturur."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google giriş yapılandırması eksik (GOOGLE_CLIENT_ID)."
        )

    try:
        google_payload = google_id_token.verify_oauth2_token(
            payload.id_token,
            GoogleRequest(),
            GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Geçersiz Google kimlik bilgisi")

    email = (google_payload.get("email") or "").lower().strip()
    email_verified = bool(google_payload.get("email_verified"))

    if not email or not email_verified:
        raise HTTPException(status_code=401, detail="Doğrulanmış email bilgisi alınamadı")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        # Uygulamada password_hash zorunlu olduğu için rastgele bir hash atanır.
        user = User(
            email=email,
            password_hash=hash_password(secrets.token_urlsafe(32))
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Mevcut kullanıcı bilgilerini getir"""
    return current_user
