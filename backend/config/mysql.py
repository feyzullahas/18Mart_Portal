import os
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

dbconfig = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "database9876"),
    "database": os.getenv("DB_NAME", "portal_db"),
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="portal_pool",
    pool_size=5,
    **dbconfig
)

def get_mysql_connection():
    return connection_pool.get_connection()
