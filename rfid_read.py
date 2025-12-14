from pirc522 import RFID
import time

rdr = RFID(bus=0, device=0)

print("RC522 ready (Raspberry Pi 5)")
print("Scan a card...")

try:
    while True:
        rdr.wait_for_tag()
        (err, _) = rdr.request()
        if not err:
            (err, uid) = rdr.anticoll()
            if not err:
                print("Card UID:", uid)
                time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting")

finally:
    rdr.cleanup()
