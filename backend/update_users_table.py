from config.mysql import get_mysql_connection

conn = get_mysql_connection()
cursor = conn.cursor()

# Add missing columns to users table
try:
    cursor.execute("ALTER TABLE users ADD COLUMN username VARCHAR(50) UNIQUE AFTER email")
    print("Added username column")
except Exception as e:
    print(f"Username column already exists or error: {e}")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN full_name VARCHAR(100) NOT NULL DEFAULT '' AFTER username")
    print("Added full_name column")
except Exception as e:
    print(f"Full_name column already exists or error: {e}")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN student_id VARCHAR(20) UNIQUE AFTER full_name")
    print("Added student_id column")
except Exception as e:
    print(f"Student_id column already exists or error: {e}")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN department VARCHAR(100) NOT NULL DEFAULT '' AFTER student_id")
    print("Added department column")
except Exception as e:
    print(f"Department column already exists or error: {e}")

conn.commit()

# Show updated table structure
cursor.execute('DESCRIBE users')
print('\nUpdated users table structure:')
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()
