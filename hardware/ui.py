"""
Name: Töökoja haldussüsteem UI
Kirjeldus: Script for UI.
Autor: Helar Pullisaar
Date: 04.12.2025
Version: 1.0
"""

# Import necessary modules
import tkinter as tk
from tkinter import ttk
import threading
import time
from tkinter import simpledialog
import sqlite3

USER_DB_PATH = "data/data/users.db"
TOOLS_DB_PATH = "data/data/tools.db"

def get_borrowed_tools(user_uid):
    conn = sqlite3.connect(TOOLS_DB_PATH)
    c = conn.cursor()
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
    conn.commit()
    conn.close()

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

# =========================
# UI CLASSES
# =========================

class App(tk.Tk):
    # Initialize the main application window
    def __init__(self):
        super().__init__()

        self.title("Tookoja haldusysteem")
        self.geometry("800x480") #Window size

        # Container for all pages
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.pages = {}

        # Register pages
        for Page in (HomePage, UserAuthPage, UserRegPage, UserPage, BorrowToolPage):
            page = Page(self.container, self)
            self.pages[Page] = page
            page.place(relwidth=1, relheight=1)

        self.show(HomePage)

    def shutdown(self):
        for page in self.pages.values():
            if hasattr(page, "stop_polling"):
                page.stop_polling = True
        self.destroy()

    def show(self, page):
        self.pages[page].tkraise()

        # Start registration if UserRegPage
        if page == UserRegPage:
            rfid = getattr(self, "rfid", None)
            if rfid:
                self.pages[UserRegPage].start_registration(self, rfid)

        # Start authentication if UserAuthPage
        if page == UserAuthPage:
            rfid = getattr(self, "rfid", None)
            if rfid:
                self.pages[UserAuthPage].start_auth(self, rfid)

        # Start borrow polling if BorrowToolPage
        if page == BorrowToolPage:
            rfid = getattr(self, "rfid", None)
            if rfid:
                self.pages[BorrowToolPage].start_borrow(self, rfid)

        # Refresh borrowed tools if UserPage
        if page == UserPage:
            self.pages[UserPage].update_borrowed_tools()


# =========================
# PAGES
# =========================

# Home Page
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Siit kapist saad töökoja võtme, et kasutada ja laenutada tööriistu kuni 24 tunniks.",
                  wraplength=700, font=("Arial", 16)).pack(pady=40)
        
        ttk.Button(self, text="Kasutaja tuvastamine",
                   command=lambda: controller.show(UserAuthPage)).pack(pady=10)

        ttk.Button(self, text="Registreeri uus kasutaja", command=lambda: controller.show(UserRegPage)).pack(pady=0)

# User Authentication Page
class UserAuthPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.polling_thread = None
        self.stop_polling = False

        ttk.Label(self, text="Kasutaja tuvastamiseks viipa kaarti!",
                  wraplength=700, font=("Arial", 16)).pack(pady=40)

        self.status_label = ttk.Label(self, text="", font=("Arial", 14))
        self.status_label.pack(pady=20)

        ttk.Button(self, text="Tagasi avalehele",
                   command=self.go_home).pack(pady=20)

    def update_message(self, text):
        self.status_label.config(text=text)
        self.update()  # force UI refresh

    def go_home(self):
        self.stop_polling = True
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(0.1)
        self.controller.show(HomePage)

    def start_auth(self, app, rfid):
        """Start background polling for user authentication"""
        self.stop_polling = False
        self.update_message("Hold your card near the reader...")

        def poll():
            while not self.stop_polling:
                uid_bytes = rfid.read_uid()
                if uid_bytes:
                    uid_str = ":".join(f"{b:02X}" for b in uid_bytes)
                    # Schedule authentication in main thread
                    # Use self.controller.show() instead of app.show()
                    self.after(0, lambda: self.authenticate_user(uid_str))
                    break
                time.sleep(0.2)

        self.polling_thread = threading.Thread(target=poll, daemon=True)
        self.polling_thread.start()

    def authenticate_user(self, uid_str):
        """Check if user exists and navigate to UserPage"""
        user = get_user_by_uid(uid_str)
        if user:
            self.update_message(f"Welcome {user[1]}!")
            
            # Save the authenticated user UID to App
            self.controller.current_user_uid = uid_str

            # Navigate using controller (your App instance)
            self.after(500, lambda: self.controller.show(UserPage))
        else:
            self.update_message(f"UID {uid_str} not registered.")

        
# New User Registration Page
class UserRegPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.polling_thread = None
        self.stop_polling = False

        self.status_label = ttk.Label(self, text="", font=("Arial", 14))
        self.status_label.pack(pady=20)

        ttk.Button(self, text="Tagasi avalehele",
                   command=self.go_home).pack(pady=20)

    def update_message(self, text):
        self.status_label.config(text=text)
        self.update()  # force UI update

    def go_home(self):
        self.stop_polling = True
        self.controller.show(HomePage)

    def start_registration(self, app, rfid):
        self.stop_polling = False
        self.update_message("Scan a new RFID card...")

        def poll():
            while not self.stop_polling:
                uid_bytes = rfid.read_uid()
                if uid_bytes:
                    uid_str = ":".join(f"{b:02X}" for b in uid_bytes)
                    # Schedule GUI input on main thread
                    app.after(0, lambda: self.register_user(app, uid_str))
                    break
                time.sleep(0.2)

        self.polling_thread = threading.Thread(target=poll, daemon=True)
        self.polling_thread.start()

    def register_user(self, app, uid_str):
        # Ask for name (main thread safe)
        name = simpledialog.askstring("Sisesta nimi", f"Enter name for UID {uid_str}:")
        if name:
            add_user(uid_str, name)
            self.update_message(f"User {name} registered with UID {uid_str}!")

            # Save UID as current user
            self.controller.current_user_uid = uid_str

            # Automatically go to UserPage
            self.after(500, lambda: self.controller.show(UserPage))
        else:
            self.update_message("Registration cancelled.")
        

# User Main Page        
class UserPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(
            self,
            text="Your borrowed tools:",
            font=("Arial", 16)
        ).pack(pady=20)

        self.status_label = ttk.Label(self, text="", font=("Arial", 14))
        self.status_label.pack(pady=5)

        self.tool_listbox = tk.Listbox(
            self, width=50, height=8, font=("Arial", 14)
        )
        self.tool_listbox.pack(pady=10)

        ttk.Button(
            self, text="Borrow Tool",
            command=lambda: controller.show(BorrowToolPage)
        ).pack(pady=5)

        ttk.Button(
            self, text="Log Out",
            command=lambda: controller.show(HomePage)
        ).pack(pady=5)

        ttk.Button(
            self,
            text="Open Locker",
            command=lambda: self.controller.open_lock()
        ).pack(pady=10)


    # -------------------------
    # UI helpers
    # -------------------------
    def update_message(self, text):
        self.status_label.config(text=text)
        self.update_idletasks()

    # -------------------------
    # Borrowed tools listing
    # -------------------------
    def update_borrowed_tools(self):
        # Remove old return buttons
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) and hasattr(widget, "is_return_button"):
                widget.destroy()

        self.tool_listbox.delete(0, tk.END)

        user_uid = getattr(self.controller, "current_user_uid", None)
        if not user_uid:
            self.tool_listbox.insert(tk.END, "No user logged in.")
            return

        tools = get_borrowed_tools(user_uid)

        if not tools:
            self.tool_listbox.insert(tk.END, "No tools borrowed.")
            return

        for name, tool_uid in tools:
            self.tool_listbox.insert(
                tk.END, f"{name} ({tool_uid})"
            )

            btn = tk.Button(
                self,
                text="Return",
                font=("Arial", 12),
                command=lambda t_uid=tool_uid: self.request_tool_return(t_uid)
            )
            btn.is_return_button = True
            btn.pack(pady=2)

    # -------------------------
    # Tool return flow
    # -------------------------
    def request_tool_return(self, expected_tool_uid):
        self.update_message("Scan the TOOL to return it...")

        # Disable return buttons while waiting
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) and hasattr(widget, "is_return_button"):
                widget.config(state="disabled")

        def poll():
            rfid = getattr(self.controller, "rfid", None)
            if not rfid:
                self.after(0, lambda: self.update_message("RFID not available"))
                return

            while True:
                uid_bytes = rfid.read_uid()
                if uid_bytes:
                    scanned_uid = ":".join(f"{b:02X}" for b in uid_bytes)
                    self.after(
                        0,
                        lambda: self.verify_tool_return(expected_tool_uid, scanned_uid)
                    )
                    break
                time.sleep(0.2)

        threading.Thread(target=poll, daemon=True).start()

    def verify_tool_return(self, expected_tool_uid, scanned_uid):
        if scanned_uid != expected_tool_uid:
            self.update_message("Wrong tool scanned! Try again.")
            self.update_borrowed_tools()
            return

        user_uid = self.controller.current_user_uid

        mark_tool_returned(user_uid, expected_tool_uid)
        self.update_message("Tool returned successfully!")
        self.update_borrowed_tools()


# Borrow Tool Page
class BorrowToolPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.polling_thread = None
        self.stop_polling = False

        ttk.Label(self, text="Place the tool near the reader to borrow",
                  wraplength=700, font=("Arial", 16)).pack(pady=40)

        self.status_label = ttk.Label(self, text="", font=("Arial", 14))
        self.status_label.pack(pady=20)

        ttk.Button(self, text="Back to Home", command=self.go_home).pack(pady=20)

    def update_message(self, text):
        self.status_label.config(text=text)
        self.update()

    def go_home(self):
        self.stop_polling = True
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(0.1)
        self.controller.show(HomePage)

    def start_borrow(self, app, rfid):
        """Start polling for a tool RFID"""
        self.stop_polling = False
        self.update_message("Scan the tool RFID...")

        def poll():
            while not self.stop_polling:
                uid_bytes = rfid.read_uid()
                if uid_bytes:
                    uid_str = ":".join(f"{b:02X}" for b in uid_bytes)
                    app.after(0, lambda: self.borrow_tool(app, uid_str))
                    break
                time.sleep(0.2)

        self.polling_thread = threading.Thread(target=poll, daemon=True)
        self.polling_thread.start()

    def borrow_tool(self, app, tool_uid):
        """Check tool in DB and mark as borrowed by current user"""

        if not getattr(app, "current_user_uid", None):
            self.update_message("No authenticated user!")
            return

        tool = get_tool_by_uid(tool_uid)
        if tool:
            mark_tool_borrowed(app.current_user_uid, tool_uid)
            self.update_message(f"Tool '{tool[1]}' borrowed successfully!")

            # After short delay, go back to UserPage
            self.after(1000, lambda: self.controller.show(UserPage))
        else:
            self.update_message(f"Tool UID {tool_uid} not found!")


# =========================
# STANDALONE TEST MODE
# =========================

def run_ui():
    """Run the UI standalone without any hardware"""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    print("Standalone UI test mode – no hardware required")
    run_ui()
