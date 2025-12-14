from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

reader = SimpleMFRC522()

print("RC522 RFID reader ready")
print("Place your card near the reader...")

try:
    while True:
        uid, text = reader.read()
        print("UID:", uid)
        print("Text:", text)
        print("-" * 30)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()
