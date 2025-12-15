from periphery import GPIO
import spidev
from time import sleep

# ----------------------------
# Helper functions
# ----------------------------

def write_reg(spi, addr, val):
    spi.xfer([(addr << 1) & 0x7E, val])

def read_reg(spi, addr):
    return spi.xfer([((addr << 1) & 0x7E) | 0x80, 0])[1]

def reset_reader(spi, rst, COMMAND):
    """Toggle RST and soft reset RC522"""
    rst.write(False)
    sleep(0.05)
    rst.write(True)
    sleep(0.05)
    write_reg(spi, COMMAND, 0x0F)
    sleep(0.05)

# ----------------------------
# Setup
# ----------------------------

# GPIO for RST
rst = GPIO("/dev/gpiochip0", 25, "out")

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, CE0
spi.max_speed_hz = 100000  # slow for reliability
sleep(0.05)  # allow SPI to stabilize

# RC522 registers
FIFO, COMMAND, BIT_FRAMING, ERROR_REG = 0x09, 0x01, 0x0D, 0x06
REQIDL, ANTICOLL = 0x26, 0x93

# Initialize RC522
reset_reader(spi, rst, COMMAND)
print("Hold card near the reader...")

# ----------------------------
# Main loop
# ----------------------------
try:
    while True:
        # ----------------
        # Request card
        # ----------------
        write_reg(spi, BIT_FRAMING, 0x07)
        write_reg(spi, FIFO, REQIDL)
        write_reg(spi, COMMAND, 0x0C)
        sleep(0.02)
        error = read_reg(spi, ERROR_REG)

        # ----------------
        # Anticollision: read UID
        # ----------------
        write_reg(spi, BIT_FRAMING, 0x00)
        write_reg(spi, FIFO, ANTICOLL)
        write_reg(spi, COMMAND, 0x0C)
        sleep(0.02)
        uid = [read_reg(spi, FIFO) for _ in range(5)]

        print(f"ERROR_REG: 0x{error:02X}, UID bytes: {uid}")

        # ----------------
        # If no card detected, retry reset
        # ----------------
        if error != 0x00 or all(b == 0 for b in uid):
            print("No card detected, resetting RC522...")
            reset_reader(spi, rst, COMMAND)

        sleep(0.05)  # loop delay

except KeyboardInterrupt:
    print("Exiting, cleaning up...")

finally:
    spi.close()
    rst.close()
