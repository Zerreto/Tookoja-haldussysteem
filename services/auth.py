# services/auth.py
import sqlite3

DB_PATH = "data/users.db"

def is_authorized(uid: str) -> bool:
    """
    Check if a scanned UID is authorized.
    Returns True if UID exists in the database.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE uid = ?", (uid,))
        result = cursor.fetchone()
        conn.close()
        return result[0] > 0
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
