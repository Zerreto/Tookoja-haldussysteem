from periphery import GPIO
import spidev
from time import sleep

# Use GPIO chip and line for RST (line 25 = BCM25)
rst = GPIO("/dev/gpiochip0", 25, "out")
rst.write(True)

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 500000  # safe for RC522

# RC522 registers
FIFO, COMMAND, BIT_FRAMING, ERROR_REG = 0x09, 0x01, 0x0D, 0x06
REQIDL, ANTICOLL = 0x26, 0x93

def write_reg(addr, val):
    spi.xfer([(addr << 1) & 0x7E, val])

def read_reg(addr):
    return spi.xfer([((addr << 1) & 0x7E) | 0x80, 0])[1]

# Reset RC522
write_reg(COMMAND, 0x0F)
sleep(0.05)

last_uid = None
print("Hold card near reader...")

try:
    while True:
        # Request card
        write_reg(BIT_FRAMING, 0x07)
        write_reg(FIFO, REQIDL)
        write_reg(COMMAND, 0x0C)
        sleep(0.02)

        if read_reg(ERROR_REG) == 0:
            # Card detected, read UID
            write_reg(BIT_FRAMING, 0x00)
            write_reg(FIFO, ANTICOLL)
            write_reg(COMMAND, 0x0C)
            sleep(0.02)
            uid = [read_reg(FIFO) for _ in range(5)]

            if uid != last_uid:
                print("Card UID:", uid)
                last_uid = uid
        else:
            last_uid = None

        sleep(0.02)  # ~50 reads/sec
except KeyboardInterrupt:
    spi.close()
    rst.close()
    print("Exit.")
