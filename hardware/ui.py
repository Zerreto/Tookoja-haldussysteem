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
        for Page in (HomePage, UserAuthPage, UserRegPage, UserPage):
            page = Page(self.container, self)
            self.pages[Page] = page
            page.place(relwidth=1, relheight=1)

        self.show(HomePage)

    def show(self, page):
        self.pages[page].tkraise()
        if page == UserRegPage:
            rfid = getattr(self, "rfid", None)
            if rfid:
                self.pages[UserRegPage].start_registration(self, rfid)


# =========================
# PAGES
# =========================

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

        ttk.Label(self, text="Kasutaja tuvastamiseks viipa kaarti!",
                  wraplength=700, font=("Arial", 16)).pack(pady=40)

        
        ttk.Button(self, text="Tagasi avalehele",
                   command=lambda: controller.show(HomePage)).pack(pady=20)
        

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

        
        #ttk.Button(self, text="Tööriistade laenutamine",
         #          command=lambda: controller.show(BorrowPage)).pack(pady=0)

        #ttk.Button(self, text="Tööriistade tagastamine",
          #         command=lambda: controller.show(ReturnPage)).pack(pady=0)
        
        #ttk.Button(self, text="Ava võtme kapp",
         #          command=lambda: controller.show(ReturnPage)).pack(pady=0)
        
        ttk.Button(self, text="Logi välja",
                   command=lambda: controller.show(HomePage)).pack(pady=20)


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
