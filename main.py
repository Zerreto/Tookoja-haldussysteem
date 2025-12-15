from hardware.rfid import RFIDReader
from hardware.ui import App, UserPage
from services.auth import is_authorized
from threading import Thread
from time import sleep

def rfid_loop(app, rfid):
    while True:
        uid = rfid.read_uid()
        if uid:
            uid_str = ":".join(f"{b:02X}" for b in uid)
            if is_authorized(uid_str):
                app.show(UserPage)
                print(f"[ACCESS GRANTED] UID: {uid_str}")
            else:
                print(f"[ACCESS DENIED] UID: {uid_str}")
            sleep(1)
        sleep(0.1)

def main():
    # Initialize RFID
    rfid = RFIDReader()

    # Initialize UI
    app = App()

    # Start RFID polling in background
    Thread(target=rfid_loop, args=(app, rfid), daemon=True).start()

    # Run UI loop
    try:
        app.mainloop()
    finally:
        rfid.close()
        print("System shutdown")

# Program entry point
if __name__ == "__main__":
    main()
