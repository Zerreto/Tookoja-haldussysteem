import sqlite3

conn = sqlite3.connect("data/users.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uid TEXT UNIQUE NOT NULL,
    name TEXT
)
""")

conn.commit()
conn.close()
print("Database created successfully.")
