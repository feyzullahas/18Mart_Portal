from config.mysql import get_mysql_connection

conn = get_mysql_connection()
cursor = conn.cursor()

# Remove unnecessary columns from users table
try:
    cursor.execute("ALTER TABLE users DROP COLUMN username")
    print("Removed username column")
except Exception as e:
    print(f"Username column doesn't exist or error: {e}")

try:
    cursor.execute("ALTER TABLE users DROP COLUMN full_name")
    print("Removed full_name column")
except Exception as e:
    print(f"Full_name column doesn't exist or error: {e}")

try:
    cursor.execute("ALTER TABLE users DROP COLUMN student_id")
    print("Removed student_id column")
except Exception as e:
    print(f"Student_id column doesn't exist or error: {e}")

try:
    cursor.execute("ALTER TABLE users DROP COLUMN department")
    print("Removed department column")
except Exception as e:
    print(f"Department column doesn't exist or error: {e}")

conn.commit()

# Show updated table structure
cursor.execute('DESCRIBE users')
print('\nFinal users table structure:')
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
