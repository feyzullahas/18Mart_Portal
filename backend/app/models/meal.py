from pydantic import BaseModel
from typing import List, Optional

class MealItem(BaseModel):
    name: str
    calories: Optional[int] = None
    is_side: bool = False  # Yan yemek mi?

class DailyMenu(BaseModel):
    date: str
    breakfast: List[MealItem] = []
    dinner: List[MealItem] = []
    total_calories_dinner: Optional[int] = None

class OsemMenu(BaseModel):
    date: str
    menu: List[MealItem] = []
    total_calories: Optional[int] = None
