import tkinter as tk
from tkinter import ttk

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
        for Page in (HomePage, UserPage, BorrowPage, ReturnPage):
            page = Page(self.container, self)
            self.pages[Page] = page
            page.place(relwidth=1, relheight=1)

        self.show(HomePage)

    def show(self, page):
        """Bring the selected page to front"""
        self.pages[page].tkraise()


# =========================
# PAGES
# =========================

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Siit kapist saad töökoja võtme, et kasutada ja laenutada tööriistu kuni 24 tunniks.",
                  wraplength=700, font=("Arial", 16)).pack(pady=40)

        ttk.Button(self, text="Kasutaja tuvastamine",
                   command=lambda: controller.show(UserPage)).pack(pady=10)

        ttk.Button(self, text="Tööriistade laenutamine",
                   command=lambda: controller.show(BorrowPage)).pack(pady=0)

        ttk.Button(self, text="Tööriistade tagastamine",
                   command=lambda: controller.show(ReturnPage)).pack(pady=0)


class UserPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Kasutaja tuvastamiseks viipa kaarti!",
                  wraplength=700, font=("Arial", 16)).pack(pady=40)

        self.status_label = ttk.Label(self, text="", font=("Arial", 14))
        self.status_label.pack(pady=20)

        # Keep a reference to the button
        self.register_button = ttk.Button(self, text="Registreeri uus kasutaja")
        self.register_button.pack(pady=20)

        ttk.Button(self, text="Tagasi avalehele",
                   command=lambda: controller.show(HomePage)).pack(pady=20)
        
    def update_message(self, text):
        self.status_label.config(text=text)
        
    # Placeholder for main.py to connect
    def on_register(self):
        """To be overridden in main.py"""
        pass


class BorrowPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Tööriistade laenutamine",
                  wraplength=700, font=("Arial", 16)).pack(pady=40)

        ttk.Button(self, text="Tagasi avalehele",
                   command=lambda: controller.show(HomePage)).pack(pady=20)


class ReturnPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Tööriistade tagastamine",
                  wraplength=700, font=("Arial", 16)).pack(pady=40)

        ttk.Button(self, text="Tagasi avalehele",
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
