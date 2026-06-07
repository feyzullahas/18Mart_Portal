from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.meal_rating import MealRating
from app.models.user import User
from app.routers.auth_new import get_current_user, SECRET_KEY, ALGORITHM
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date as date_type
from jose import jwt, JWTError

router = APIRouter(prefix="/meal-ratings", tags=["meal-ratings"])

# Token olmasa da hata vermeyen opsiyonel scheme
oauth2_optional = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_optional),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Token varsa kullanıcıyı döndür, yoksa None."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        email: str = payload.get("sub")
        if not user_id or not email:
            return None
        user = db.query(User).filter(User.id == int(user_id), User.email == email).first()
        return user
    except (JWTError, Exception):
        return None


class RatingCreate(BaseModel):
    cafeteria: str = Field(..., pattern="^(kyk_kahvalti|kyk_aksam|osem)$")
    date: str  # "YYYY-MM-DD"
    rating: int = Field(..., ge=1, le=5)


class RatingResponse(BaseModel):
    average: Optional[float]
    count: int
    user_rating: Optional[int]  # Kullanıcının kendi oyu (varsa)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def submit_rating(
    data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bugünkü yemek puanını kaydet. Daha önce oy verdiyse hata döndür."""

    # Sadece bugünün tarihine oy verilebilir
    today_str = str(date_type.today())
    if data.date != today_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece bugünün yemeği için puan verebilirsiniz.",
        )

    # Daha önce oy vermiş mi kontrol et
    existing = (
        db.query(MealRating)
        .filter(
            MealRating.user_id == current_user.id,
            MealRating.cafeteria == data.cafeteria,
            MealRating.date == data.date,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bu yemekhane için bugün zaten oy kullandınız.",
        )

    new_rating = MealRating(
        user_id=current_user.id,
        cafeteria=data.cafeteria,
        date=data.date,
        rating=data.rating,
    )
    db.add(new_rating)
    db.commit()

    return {"message": "Oyunuz kaydedildi."}


@router.get("/{cafeteria}/{date}", response_model=RatingResponse)
async def get_ratings(
    cafeteria: str,
    date: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Belirtilen yemekhane + tarih için ortalama puan ve oy sayısını döndürür."""

    result = (
        db.query(func.avg(MealRating.rating), func.count(MealRating.id))
        .filter(MealRating.cafeteria == cafeteria, MealRating.date == date)
        .first()
    )

    avg_rating, count = result
    average = round(float(avg_rating), 1) if avg_rating is not None else None

    # Kullanıcının kendi oyu
    user_rating = None
    if current_user:
        user_vote = (
            db.query(MealRating)
            .filter(
                MealRating.user_id == current_user.id,
                MealRating.cafeteria == cafeteria,
                MealRating.date == date,
            )
            .first()
        )
        if user_vote:
            user_rating = user_vote.rating

    return RatingResponse(average=average, count=count, user_rating=user_rating)
