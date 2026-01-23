import mysql.connector
from mysql.connector import Error

def get_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Feyzo.1551",
            database="portal_db"
        )
        return connection

    except Error as e:
        print("❌ MySQL bağlantı hatası:", e)
        return None
