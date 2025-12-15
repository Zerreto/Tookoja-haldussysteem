import tkinter as tk
from tkinter import ttk
import threading
import time
from tkinter import simpledialog

# =========================
# UI CLASSES
# =========================

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Tookoja haldusysteem")
        self.geometry("800x480")

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

import tkinter as tk
from tkinter import ttk
import threading
import time

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
        from main import get_tool_by_uid, mark_tool_borrowed

        if not getattr(app, "current_user_uid", None):
            self.update_message("No authenticated user!")
            return

        tool = get_tool_by_uid(tool_uid)
        if tool:
            mark_tool_borrowed(app.current_user_uid, tool_uid)
            self.update_message(f"Tool '{tool[1]}' borrowed successfully!")
        else:
            self.update_message(f"Tool UID {tool_uid} not found!")


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Siit kapist saad töökoja võtme, et kasutada ja laenutada tööriistu kuni 24 tunniks.",
                  wraplength=700, font=("Arial", 16)).pack(pady=40)
        
        ttk.Button(self, text="Kasutaja tuvastamine",
                   command=lambda: controller.show(UserAuthPage)).pack(pady=10)

        ttk.Button(self, text="Registreeri uus kasutaja", command=lambda: controller.show(UserRegPage)).pack(pady=0)


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
        from main import get_user_by_uid  # or your DB module
        user = get_user_by_uid(uid_str)
        if user:
            self.update_message(f"Welcome {user[1]}!")
            
            # Save the authenticated user UID to App
            self.controller.current_user_uid = uid_str

            # Navigate using controller (your App instance)
            self.after(500, lambda: self.controller.show(UserPage))
        else:
            self.update_message(f"UID {uid_str} not registered.")


        

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
            from main import add_user  # adjust if using a separate db module
            add_user(uid_str, name)
            self.update_message(f"User {name} registered with UID {uid_str}!")
        else:
            self.update_message("Registration cancelled.")
        
class UserPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Welcome! Here are your borrowed tools:", font=("Arial", 16)).pack(pady=20)

        # Listbox to show borrowed tools
        self.tool_listbox = tk.Listbox(self, width=50, height=10, font=("Arial", 14))
        self.tool_listbox.pack(pady=10)

        ttk.Button(self, text="Borrow Tool",
                   command=lambda: controller.show(BorrowToolPage)).pack(pady=10)

        ttk.Button(self, text="Log Out", command=lambda: controller.show(HomePage)).pack(pady=10)

    def update_borrowed_tools(self):
        """Fetch and display borrowed tools for the current user."""
        self.tool_listbox.delete(0, tk.END)
        uid = getattr(self.controller, "current_user_uid", None)
        if uid:
            from main import get_borrowed_tools
            tools = get_borrowed_tools(uid)
            if tools:
                for name, tool_uid in tools:
                    self.tool_listbox.insert(tk.END, f"{name} ({tool_uid})")
            else:
                self.tool_listbox.insert(tk.END, "No tools borrowed.")
        else:
            self.tool_listbox.insert(tk.END, "No user logged in.")



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
