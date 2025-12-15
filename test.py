from hardware.rfid import RFIDReader
from time import sleep

r = RFIDReader()
print("RC522 initialized OK")

try:
    while True:
        uid = r.read_uid()
        if uid:
            print("UID:", ":".join(f"{b:02X}" for b in uid))
            sleep(1)
except KeyboardInterrupt:
    r.close()