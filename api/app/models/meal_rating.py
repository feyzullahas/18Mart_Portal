from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class MealRating(Base):
    __tablename__ = "meal_ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cafeteria = Column(String(20), nullable=False)   # "kyk_kahvalti", "kyk_aksam", "osem"
    date = Column(String(12), nullable=False)        # "2026-06-07" formatı
    rating = Column(Integer, nullable=False)         # 1-5

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Bir kullanıcı, bir yemekhane için günde yalnızca bir kez oy kullanabilir
    __table_args__ = (
        UniqueConstraint("user_id", "cafeteria", "date", name="uq_user_cafeteria_date"),
    )
