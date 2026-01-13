"""
Name: Töökoja haldussüsteem
Kirjeldus: Main script for borrowing tools using RFID and opening a solenoid lock.
Autor: Helar Pullisaar
Date: 04.12.2025
Version: 1.0
"""

# Import necessary modules
from hardware.rfid import RFIDReader
from hardware.ui import App, UserRegPage
import sqlite3
from threading import Thread
from time import sleep
from tkinter import simpledialog
from periphery import GPIO
import time
# Database paths
USER_DB_PATH = "data/users.db"
TOOLS_DB_PATH = "data/tools.db"

LOCK_PIN = 18  # GPIO pin for solenoid lock

# Initialize GPIO once
lock_gpio = GPIO(f"/dev/gpiochip0", LOCK_PIN, "out")
lock_gpio.write(False)  # default LOW = locked

def open_lock(duration=5):
    """Activate solenoid to unlock for a short duration (seconds)."""
    print("open lock")
    #lock_gpio.write(True)   # energize solenoid
    #sleep(duration)         # keep lock open
    #lock_gpio.write(False)  # lock again

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
    print("add user")
    #conn = sqlite3.connect(USER_DB_PATH)
    #c = conn.cursor()
    #c.execute("INSERT OR IGNORE INTO users (uid, name) VALUES (?, ?)", (uid, name))
    #conn.commit()
    #conn.close()


# Main program logic
def main():
    # Initialize RFID
    try:
        time.sleep(1)
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
