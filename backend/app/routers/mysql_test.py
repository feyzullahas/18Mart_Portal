from fastapi import APIRouter
from config.mysql import get_mysql_connection

router = APIRouter(
    prefix="/mysql",
    tags=["MySQL Test"]
)

@router.get("/ping")
def mysql_ping():
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return {
        "mysql": "connected",
        "result": result
    }
