# Import standard libraries
import tkinter as tk
from tkinter import ttk
# import threading
# import time
# import platform

# -----------------------------
# Detect Platform
# -----------------------------
# IS_RPI = platform.system() == "Linux"  # Raspberry Pi usually reports 'Linux'

# # -----------------------------
# # Raspberry Pi Hardware Setup
# # -----------------------------
# if IS_RPI:
#     import RPi.GPIO as GPIO
#     from mfrc522 import SimpleMFRC522

#     # Solenoid lock pin
#     SOLENOID_LOCK_PIN = 17
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(SOLENOID_LOCK_PIN, GPIO.OUT)

#     def solenoid_lock_on():
#         GPIO.output(SOLENOID_LOCK_PIN, GPIO.HIGH)

#     def solenoid_lock_off():
#         GPIO.output(SOLENOID_LOCK_PIN, GPIO.LOW)

#     # RFID reader
#     reader = SimpleMFRC522()
# else:
#     # Windows simulation
#     def solenoid_lock_on():
#         print("[SIM] Solenoid ON")

#     def solenoid_lock_off():
#         print("[SIM] Solenoid OFF")

#     class SimpleMFRC522:
#         def read_no_block(self):
#             return None, None

#     reader = SimpleMFRC522()


# -----------------------------
# RFID Thread
# -----------------------------
# class RFIDThread:
#     def __init__(self):
#         self.running = False
#         self.thread = None

#     def start(self, callback):
#         self.running = True
#         self.thread = threading.Thread(target=self.read_loop, args=(callback,), daemon=True)
#         self.thread.start()

#     def stop(self):
#         self.running = False

#     def read_loop(self, callback):
#         if IS_RPI:
#             while self.running:
#                 try:
#                     uid, text = reader.read_no_block()
#                     if uid:
#                         callback(uid)
#                 except:
#                     pass
#                 time.sleep(0.2)
#         else:
#             # Windows simulation: just send a test UID after 1 second
#             if self.running:
#                 time.sleep(1)
#                 callback("SIMULATED_TAG_1234")


# rfid = RFIDThread()

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Tookoja haldusysteem")
        self.geometry("800x480")

        # Container that holds all pages
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.pages = {}

        # List your pages here
        for Page in (HomePage, UserPage, BorrowPage,):
            page = Page(self.container, self)
            self.pages[Page] = page
            page.place(relwidth=1, relheight=1)  # Fill the entire window

        self.show(HomePage)

    def show(self, page):
        """Bring the selected page to the front."""
        self.pages[page].tkraise()


# -----------------------------
# START PAGE
# -----------------------------
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Siit kapist saad töökoja võtme, et kasutada ja laenutada tööriistu kuni 24 tunniks.").pack(pady=40)

        ttk.Button(self, text="Kasutaja tuvastamine",
                   command=lambda: controller.show(UserPage)).pack(pady=10)
        
        ttk.Button(self, text="Tööriistade laenutamine",
                   command=lambda: controller.show(BorrowPage)).pack(pady=0)
        
        ttk.Button(self, text="Tööriistade tagastamine",
                   command=lambda: controller.show(BorrowPage)).pack(pady=0)


# -----------------------------
# PAGE 1
# -----------------------------
class UserPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Kasutaja tuvastamiseks viipa kaarti!").pack(pady=40)

        ttk.Button(self, text="Registreeri uus kasutaja",
                   command=lambda: controller.show(HomePage)).pack(pady=20)
        
        ttk.Button(self, text="Tagasi avalehele",
                   command=lambda: controller.show(HomePage)).pack(pady=20)

    # def start_rfid(self):
    #     self.output.config(text="Scan RFID...")
    #     rfid.start(self.show_uid)

    # def stop_rfid(self):
    #     rfid.stop()

    # def show_uid(self, uid):
    #     """Called when a tag is detected"""
    #     self.output.config(text=f"Card UID: {uid}")

# -----------------------------
# PAGE 2
# -----------------------------
class BorrowPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Tööriistade laenutamine").pack(pady=40)

        ttk.Button(self, text="Tagasi avalehele",
                   command=lambda: controller.show(HomePage)).pack(pady=20)
        

# -----------------------------
# PAGE 3
# -----------------------------
class BorrowPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Tööriistade tagastamine").pack(pady=40)

        ttk.Button(self, text="Tagasi avalehele",
                   command=lambda: controller.show(HomePage)).pack(pady=20)
        
# Open solenoid lock
# def solenoid_lock_open():
#     GPIO.output(SOLENOID_LOCK_PIN, GPIO.HIGH)

# # Close solenoid lock
# def solenoid_lock_close():
#     GPIO.output(SOLENOID_LOCK_PIN, GPIO.LOW)


# Main function
def main():
    App().mainloop()


# --------------------------
# PROGRAM ENTRY POINT
# --------------------------
if __name__ == "__main__":
    main()