import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Feyzo.1551",
        database="portal_db"
    )

    if connection.is_connected():
        print("✅ MySQL bağlantısı başarılı")

except mysql.connector.Error as err:
    print("❌ MySQL bağlantı hatası")
    print(err)

finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
