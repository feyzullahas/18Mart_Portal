from config.mysql import get_mysql_connection

conn = get_mysql_connection()

if conn:
    print("✅ mysql.py üzerinden bağlantı başarılı")
    conn.close()
else:
    print("❌ bağlantı kurulamadı")
