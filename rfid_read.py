from periphery import GPIO
import spidev
from time import sleep

# RST pin
rst = GPIO("/dev/gpiochip0", 25, "out")

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, CE0
spi.max_speed_hz = 100000  # slow for reliability

# RC522 registers
FIFO, COMMAND, BIT_FRAMING, ERROR_REG = 0x09, 0x01, 0x0D, 0x06
REQIDL, ANTICOLL = 0x26, 0x93

def write_reg(addr, val):
    spi.xfer([(addr << 1) & 0x7E, val])

def read_reg(addr):
    return spi.xfer([((addr << 1) & 0x7E) | 0x80, 0])[1]

def reset_reader():
    rst.write(False)
    sleep(0.05)
    rst.write(True)
    sleep(0.05)
    write_reg(COMMAND, 0x0F)
    sleep(0.05)

# Initialize
reset_reader()
print("Hold card near the reader...")

try:
    while True:
        # Request card
        write_reg(BIT_FRAMING, 0x07)
        write_reg(FIFO, REQIDL)
        write_reg(COMMAND, 0x0C)
        sleep(0.02)
        error = read_reg(ERROR_REG)

        # Anticollision (read UID) regardless of error
        write_reg(BIT_FRAMING, 0x00)
        write_reg(FIFO, ANTICOLL)
        write_reg(COMMAND, 0x0C)
        sleep(0.02)
        uid = [read_reg(FIFO) for _ in range(5)]

        print(f"ERROR_REG: 0x{error:02X}, UID bytes: {uid}")
        sleep(0.05)

except KeyboardInterrupt:
    spi.close()
    rst.close()
    print("Exit.")
