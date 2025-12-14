from periphery import GPIO
import spidev
from time import sleep, time

# Use GPIO chip and line for RST
rst = GPIO("/dev/gpiochip0", 25, "out")
rst.write(True)

# SPI setup
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 100000  # safe for reliable detection

# RC522 registers and commands
FIFO, COMMAND, BIT_FRAMING, ERROR_REG = 0x09, 0x01, 0x0D, 0x06
REQIDL, ANTICOLL = 0x26, 0x93

def write_reg(addr, val):
    spi.xfer([(addr << 1) & 0x7E, val])
    print(f"[DEBUG] Write 0x{val:02X} -> Reg 0x{addr:02X}")

def read_reg(addr):
    val = spi.xfer([((addr << 1) & 0x7E) | 0x80, 0])[1]
    print(f"[DEBUG] Read 0x{val:02X} <- Reg 0x{addr:02X}")
    return val

# Reset reader
write_reg(COMMAND, 0x0F)
sleep(0.05)
print("[DEBUG] Reader reset done")

last_uid = None
print("Hold card near reader...")

try:
    while True:
        print(f"[DEBUG] Loop start, time={time():.2f}")

        # Request card
        write_reg(BIT_FRAMING, 0x07)
        write_reg(FIFO, REQIDL)
        write_reg(COMMAND, 0x0C)  # Transceive
        sleep(0.02)

        error = read_reg(ERROR_REG)
        print(f"[DEBUG] ERROR_REG = 0x{error:02X}")

        if error == 0:
            print("[DEBUG] Card detected, reading UID")
            # Anticollision
            write_reg(BIT_FRAMING, 0x00)
            write_reg(FIFO, ANTICOLL)
            write_reg(COMMAND, 0x0C)
            sleep(0.02)

            uid = [read_reg(FIFO) for _ in range(5)]
            print(f"[DEBUG] Raw UID bytes: {uid}")

            if uid != last_uid:
                print("Card UID:", uid)
                last_uid = uid
        else:
            print("[DEBUG] No card detected")
            last_uid = None

        sleep(0.05)  # ~20 loops/sec
except KeyboardInterrupt:
    spi.close()
    rst.close()
    print("Exit.")
