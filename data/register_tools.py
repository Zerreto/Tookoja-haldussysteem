import sqlite3
from hardware.rfid import RFIDReader
from tkinter import Tk, simpledialog

DB_PATH = "data/tools.db"

def add_tool(uid, name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO tools (uid, name) VALUES (?, ?)", (uid, name))
    conn.commit()
    conn.close()

def main():
    rfid = RFIDReader()
    root = Tk()
    root.withdraw()  # hide Tkinter window

    print("Scan a tool RFID to register it. Press Ctrl+C to exit.")

    try:
        while True:
            uid_bytes = rfid.read_uid()
            if uid_bytes:
                uid_str = ":".join(f"{b:02X}" for b in uid_bytes)
                print(f"Detected UID: {uid_str}")
                name = simpledialog.askstring("Tool Name", f"Enter name for UID {uid_str}:")
                if name:
                    add_tool(uid_str, name)
                    print(f"Tool '{name}' registered with UID {uid_str}!")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        rfid.close()
        root.destroy()

if __name__ == "__main__":
    main()
