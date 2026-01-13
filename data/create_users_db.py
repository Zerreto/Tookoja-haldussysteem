import sqlite3
import os

USER_DB_PATH = "data/users.db"
TOOLS_DB_PATH = "data/tools.db"

# -----------------------------
# Ensure database directories exist
# -----------------------------
os.makedirs(os.path.dirname(USER_DB_PATH), exist_ok=True)
os.makedirs(os.path.dirname(TOOLS_DB_PATH), exist_ok=True)

# -----------------------------
# Ensure users table exists
# -----------------------------
def ensure_users_table():
    conn = sqlite3.connect(USER_DB_PATH)
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
    print("Users table ensured in users.db")

# -----------------------------
# Ensure tools and borrows tables exist
# -----------------------------
def ensure_tools_tables():
    conn = sqlite3.connect(TOOLS_DB_PATH)
    c = conn.cursor()
    # Tools table
    c.execute("""
    CREATE TABLE IF NOT EXISTS tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL
    )
    """)
    # Borrows table
    c.execute("""
    CREATE TABLE IF NOT EXISTS borrows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_uid TEXT NOT NULL,
        tool_uid TEXT NOT NULL,
        borrow_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        return_time TIMESTAMP,
        FOREIGN KEY(user_uid) REFERENCES users(uid),
        FOREIGN KEY(tool_uid) REFERENCES tools(uid)
    )
    """)
    conn.commit()
    conn.close()
    print("Tools and Borrows tables ensured in tools.db")

# -----------------------------
# Call these at program start
# -----------------------------
ensure_users_table()
ensure_tools_tables()
