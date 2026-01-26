import mysql.connector

def check_users():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root", 
            password="Feyzo.1551",
            database="portal_db"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM users")
        users = cursor.fetchall()
        
        print("Existing users:")
        for user in users:
            print(f"ID: {user[0]}, Email: {user[1]}")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()
