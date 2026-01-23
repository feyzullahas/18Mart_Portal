import json

from fastapi import APIRouter
from config.mysql import get_mysql_connection

router = APIRouter(prefix="/test", tags=["MySQL Test"])

@router.get("/users")
def get_users():
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, email, created_at FROM users")
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return users


@router.get("/schedule/{user_id}")
def get_schedule(user_id: int):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT data FROM schedules WHERE user_id = %s",
        (user_id,)
    )
    schedule = cursor.fetchone()

    cursor.close()
    conn.close()

    return schedule
from fastapi import Body

@router.post("/schedule/{user_id}")
def save_schedule(user_id: int, data: dict = Body(...)):
    conn = get_mysql_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO schedules (user_id, data)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE
    data = VALUES(data)
    """

    cursor.execute(query, (user_id, json.dumps(data)))

    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Ders programı kaydedildi"}
