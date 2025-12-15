from hardware.rfid import RFIDReader
from hardware.ui import App, UserRegPage
import sqlite3
from threading import Thread
from time import sleep
from tkinter import simpledialog

DB_PATH = "data/users.db"

def get_user_by_uid(uid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT uid, name FROM users WHERE uid=?", (uid,))
    result = c.fetchone()
    conn.close()
    return result

def add_user(uid, name):
    conn = sqlite3.connect(DB_PATH)
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
    rfid = RFIDReader()

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
