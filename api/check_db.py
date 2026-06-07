import sqlite3
conn = sqlite3.connect('portal_db.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", c.fetchall())
conn.close()
