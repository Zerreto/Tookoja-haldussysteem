from periphery import GPIO
import spidev
from time import sleep, time

# ================= CONFIG =================
GPIOCHIP = "/dev/gpiochip0"   # pinctrl-rp1
RST_PIN = 25                  # BCM numbering
SPI_BUS = 0
SPI_DEV = 0
SPI_SPEED = 1000000           # 1 MHz
# ==========================================

# RC522 registers
COMMAND     = 0x01
COM_IRQ     = 0x04
ERROR_REG   = 0x06
FIFO_DATA   = 0x09
FIFO_LEVEL  = 0x0A
CONTROL     = 0x0C
BIT_FRAMING = 0x0D
TX_CONTROL  = 0x14

# RC522 commands
IDLE        = 0x00
TRANSCEIVE  = 0x0C
SOFT_RESET  = 0x0F

# PICC commands
REQIDL      = 0x26
ANTICOLL    = 0x93

# ================= GPIO ====================
rst = GPIO(GPIOCHIP, RST_PIN, "out")
rst.write(True)

# ================= SPI =====================
spi = spidev.SpiDev()
spi.open(SPI_BUS, SPI_DEV)
spi.max_speed_hz = SPI_SPEED
spi.mode = 0

# ============ LOW LEVEL ====================
def write_reg(reg, val):
    spi.xfer2([(reg << 1) & 0x7E, val])

def read_reg(reg):
    return spi.xfer2([((reg << 1) & 0x7E) | 0x80, 0])[1]

def set_bits(reg, mask):
    write_reg(reg, read_reg(reg) | mask)

def clear_bits(reg, mask):
    write_reg(reg, read_reg(reg) & (~mask))

# ============ RC522 CORE ===================
def reset():
    rst.write(False)
    sleep(0.05)
    rst.write(True)
    sleep(0.05)
    write_reg(COMMAND, SOFT_RESET)
    sleep(0.05)

def antenna_on():
    if not (read_reg(TX_CONTROL) & 0x03):
        set_bits(TX_CONTROL, 0x03)

def communicate(cmd, data, timeout=0.05):
    write_reg(COMMAND, IDLE)
    write_reg(COM_IRQ, 0x7F)
    write_reg(FIFO_LEVEL, 0x80)

    for byte in data:
        write_reg(FIFO_DATA, byte)

    write_reg(COMMAND, cmd)
    if cmd == TRANSCEIVE:
        set_bits(BIT_FRAMING, 0x80)

    start = time()
    while time() - start < timeout:
        irq = read_reg(COM_IRQ)
        if irq & 0x30:
            break

    clear_bits(BIT_FRAMING, 0x80)

    if read_reg(ERROR_REG) & 0x1B:
        return None

    length = read_reg(FIFO_LEVEL)
    return [read_reg(FIFO_DATA) for _ in range(length)]

# ============ HIGH LEVEL ===================
def request():
    write_reg(BIT_FRAMING, 0x07)
    return communicate(TRANSCEIVE, [REQIDL])

def anticoll():
    write_reg(BIT_FRAMING, 0x00)
    data = communicate(TRANSCEIVE, [ANTICOLL, 0x20])
    if data and len(data) == 5:
        uid = data[:4]
        chk = uid[0] ^ uid[1] ^ uid[2] ^ uid[3]
        if chk == data[4]:
            return uid
    return None

# ============ MAIN =========================
try:
    reset()
    antenna_on()
    print("RC522 ready — scan card")

    while True:
        if request():
            uid = anticoll()
            if uid:
                print("UID:", " ".join(f"{b:02X}" for b in uid))
                sleep(1)
        sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    spi.close()
    rst.close()
