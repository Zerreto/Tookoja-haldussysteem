from pirc522 import RFID
import time

rdr = RFID()

print("RC522 ready - scan a card")

try:
    while True:
        rdr.wait_for_tag()
        (error, tag_type) = rdr.request()
        if not error:
            (error, uid) = rdr.anticoll()
            if not error:
                uid_str = " ".join(str(x) for x in uid)
                print("Card UID:", uid_str)
                time.sleep(1)

except KeyboardInterrupt:
    print("\nExiting")

finally:
    rdr.cleanup()
