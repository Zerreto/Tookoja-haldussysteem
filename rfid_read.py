from periphery import GPIO
import spidev
from time import sleep

# Setup RST
rst = GPIO("/dev/gpiochip0", 25, "out")
rst.write(True)

# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 500000

# Registers
FIFO = 0x09
COMMAND = 0x01
BIT_FRAMING = 0x0D
REQIDL = 0x26
ANTICOLL = 0x93

def write_reg(a, v): spi.xfer([(a<<1)&0x7E, v])
def read_reg(a): return spi.xfer([((a<<1)&0x7E)|0x80,0])[1]

# Simple init
write_reg(COMMAND, 0x0F)
sleep(0.05)

print("Hold a card near the reader...")

while True:
    write_reg(BIT_FRAMING, 0x07)
    write_reg(FIFO, REQIDL)
    write_reg(COMMAND, 0x0C)
    sleep(0.05)
    if read_reg(0x06)==0:  # ERROR_REG == 0 means card detected
        write_reg(BIT_FRAMING, 0x00)
        write_reg(FIFO, ANTICOLL)
        write_reg(COMMAND, 0x0C)
        sleep(0.05)
        uid = [read_reg(FIFO) for _ in range(5)]
        print("Card UID:", uid)
        break
    sleep(0.2)

spi.close()
rst.close()
