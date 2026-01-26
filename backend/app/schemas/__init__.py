from .user import UserCreate, UserLogin, UserResponse, Token, TokenData
from .course import CourseCreate, CourseUpdate, CourseResponse

# Tüm schema'ları burada export et
__all__ = [
    "UserCreate", "UserLogin", "UserResponse", "Token", "TokenData",
    "CourseCreate", "CourseUpdate", "CourseResponse"
]
