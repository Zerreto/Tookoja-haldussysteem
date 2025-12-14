"""
This Raspberry Pi code was developed by newbiely.com
This Raspberry Pi code is made available for public use without any restriction
For comprehensive instructions and wiring diagrams, please visit:
https://newbiely.com/tutorials/raspberry-pi/raspberry-pi-rfid-door-lock
"""


import RPi.GPIO as GPIO
from pirc522 import RFID
import time

# Define GPIO pins
RC522_RST_PIN = 12  # GPIO pin connected to RC522's RST pin
RELAY_PIN = 16      # GPIO pin connected to relay

# Set up GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.LOW)

# Create an instance of the RFID reader
reader = MFRC522.MFRC522()

authorized_uid = [0xFF, 0xFF, 0xFF, 0xFF]

try:
    print("Tap RFID/NFC Tag on reader")
    while True:
        (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)

        if status == reader.MI_OK:
            (status, uid) = reader.MFRC522_Anticoll()

            if status == reader.MI_OK:
                if uid == authorized_uid:
                    print("Access is granted")
                    GPIO.output(RELAY_PIN, GPIO.HIGH)  # unlock the door for 2 seconds
                    time.sleep(2)
                    GPIO.output(RELAY_PIN, GPIO.LOW)   # lock the door
                else:
                    print(f"Access denied for user with UID: {' '.join(format(b, '02x') for b in uid)}")

except KeyboardInterrupt:
    GPIO.cleanup()
