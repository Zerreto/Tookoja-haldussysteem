import tkinter as tk
from tkinter import ttk

FONT_BIG = ("Verdana", 30)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Simple Multi-Page GUI")
        self.geometry("800x480")

        # Container that holds all pages
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.pages = {}

        # List your pages here
        for Page in (StartPage, Page1, Page2):
            page = Page(self.container, self)
            self.pages[Page] = page
            page.place(relwidth=1, relheight=1)  # Fill the entire window

        self.show(StartPage)

    def show(self, page):
        """Bring the selected page to the front."""
        self.pages[page].tkraise()


# -----------------------------
# START PAGE
# -----------------------------
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Start Page", font=FONT_BIG).pack(pady=40)

        ttk.Button(self, text="Go to Page 1",
                   command=lambda: controller.show(Page1)).pack(pady=20)

        ttk.Button(self, text="Go to Page 2",
                   command=lambda: controller.show(Page2)).pack(pady=20)


# -----------------------------
# PAGE 1
# -----------------------------
class Page1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Page 1", font=FONT_BIG).pack(pady=40)

        ttk.Button(self, text="Back to Start",
                   command=lambda: controller.show(StartPage)).pack(pady=20)

        ttk.Button(self, text="Go to Page 2",
                   command=lambda: controller.show(Page2)).pack(pady=20)


# -----------------------------
# PAGE 2
# -----------------------------
class Page2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Page 2", font=FONT_BIG).pack(pady=40)

        ttk.Button(self, text="Go to Page 1",
                   command=lambda: controller.show(Page1)).pack(pady=20)

        ttk.Button(self, text="Back to Start",
                   command=lambda: controller.show(StartPage)).pack(pady=20)


# Run the app
if __name__ == "__main__":
    App().mainloop()