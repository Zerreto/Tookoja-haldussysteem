from hardware.rfid import RFIDReader
from hardware.ui import App, UserRegPage
import sqlite3
from threading import Thread
from time import sleep
from tkinter import simpledialog

USER_DB_PATH = "data/users.db"
TOOLS_DB_PATH = "data/tools.db"

def get_borrowed_tools(user_uid):
    """Return a list of tools currently borrowed by the user."""
    conn = sqlite3.connect(TOOLS_DB_PATH)
    c = conn.cursor()
    # Only show borrows that have no return_time
    c.execute("""
        SELECT t.name, t.uid
        FROM borrows b
        JOIN tools t ON b.tool_uid = t.uid
        WHERE b.user_uid = ? AND b.return_time IS NULL
    """, (user_uid,))
    tools = c.fetchall()
    conn.close()
    return tools

def get_tool_by_uid(uid):
    conn = sqlite3.connect(TOOLS_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM tools WHERE uid = ?", (uid,))
    tool = c.fetchone()
    conn.close()
    return tool

def mark_tool_borrowed(user_uid, tool_uid):
    conn = sqlite3.connect(TOOLS_DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO borrows (user_uid, tool_uid) VALUES (?, ?)", (user_uid, tool_uid))
    conn.commit()
    conn.close()

def get_user_by_uid(uid):
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT uid, name FROM users WHERE uid=?", (uid,))
    result = c.fetchone()
    conn.close()
    return result

def add_user(uid, name):
    conn = sqlite3.connect(USER_DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (uid, name) VALUES (?, ?)", (uid, name))
    conn.commit()
    conn.close()

def register_user_flow(app, rfid):
    user_reg_page = app.pages[UserRegPage]
    user_reg_page.update_message("Scan a new RFID card...")
    uid_bytes = rfid.read_uid()  # blocking read
    if not uid_bytes:
        user_reg_page.update_message("No card detected.")
        return
    uid_str = ":".join(f"{b:02X}" for b in uid_bytes)
    name = simpledialog.askstring("Sisesta nimi", f"Enter name for UID {uid_str}:")
    if not name:
        user_reg_page.update_message("Registration cancelled.")
        return
    add_user(uid_str, name)
    user_reg_page.update_message(f"User {name} registered with UID {uid_str}!")


def main():
    # Initialize RFID
    try:
        rfid = RFIDReader()
    except RuntimeError as e:
        print("RFID init failed:", e)
        raise

    # Initialize UI
    app = App()

    app.rfid = rfid





    # Run UI loop
    try:
        app.mainloop()
    finally:
        rfid.close()
        print("System shutdown")

# Program entry point
if __name__ == "__main__":
    main()
