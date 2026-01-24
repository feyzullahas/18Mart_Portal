from config.mysql import get_mysql_connection

conn = get_mysql_connection()
cursor = conn.cursor()

cursor.execute('DESCRIBE users')
print('Users table structure:')
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
