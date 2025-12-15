import spidev
from periphery import GPIO
from time import sleep, time

# ===== CONFIG =====
SPI_BUS = 0
SPI_DEV = 0  # CE0
SPI_SPEED = 500_000

RST_GPIO = 25
RST_CHIP = "/dev/gpiochip0"

# ===== RC522 REGISTERS =====
COMMAND       = 0x01
FIFO_DATA     = 0x09
FIFO_LEVEL    = 0x0A
COM_IRQ       = 0x04
ERROR_REG     = 0x06
CONTROL       = 0x0C
BIT_FRAMING   = 0x0D
MODE          = 0x11
TX_CONTROL    = 0x14
TX_AUTO       = 0x15
T_MODE        = 0x2A
T_PRESCALER   = 0x2B
T_RELOAD_H    = 0x2C
T_RELOAD_L    = 0x2D
VERSION_REG   = 0x37

# ===== COMMANDS =====
IDLE       = 0x00
SOFT_RESET = 0x0F
TRANSCEIVE = 0x0C

REQA       = 0x26
ANTICOLL   = 0x93

class RC522Debug:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(SPI_BUS, SPI_DEV)
        self.spi.max_speed_hz = SPI_SPEED
        self.spi.mode = 0

        self.rst = GPIO(RST_CHIP, RST_GPIO, "out")
        self._reset()
        self._init_rc522()

    def _write(self, reg, val):
        self.spi.xfer2([(reg << 1) & 0x7E, val])

    def _read(self, reg):
        val = self.spi.xfer2([((reg << 1) & 0x7E) | 0x80, 0])[1]
        print(f"READ reg 0x{reg:02X} -> 0x{val:02X}")  # debug
        return val

    def _reset(self):
        self.rst.write(False)
        sleep(0.2)
        self.rst.write(True)
        sleep(0.2)
        self._write(COMMAND, SOFT_RESET)
        sleep(0.2)

    def _antenna_on(self):
        if not (self._read(TX_CONTROL) & 0x03):
            self._write(TX_CONTROL, 0x03)

    def _init_rc522(self):
        try:
            self._write(T_MODE, 0x8D)
            self._write(T_PRESCALER, 0x3E)
            self._write(T_RELOAD_L, 30)
            self._write(T_RELOAD_H, 0)
            self._write(TX_AUTO, 0x40)
            self._write(MODE, 0x3D)
            self._antenna_on()

            ver = self._read(VERSION_REG)
            print(f"VERSION_REG: 0x{ver:02X}")
            if ver not in (0x91, 0x92):
                print("WARNING: RC522 not detected or invalid version!")
        except Exception as e:
            print("Init error:", e)

    def read_uid(self):
        self._write(BIT_FRAMING, 0x07)
        self._write(COM_IRQ, 0x7F)
        self._write(COMMAND, IDLE)
        # send REQA
        self._write(FIFO_DATA, REQA)
        self._write(COMMAND, TRANSCEIVE)
        self._write(BIT_FRAMING, 0x80)
        sleep(0.1)

        length = self._read(FIFO_LEVEL)
        uid = [self._read(FIFO_DATA) for _ in range(length)]
        if uid:
            print("RAW UID:", uid)
        return uid

    def close(self):
        self.spi.close()
        self.rst.close()


if __name__ == "__main__":
    rc = RC522Debug()
    print("RC522 debug – press Ctrl+C to exit")

    try:
        while True:
            uid = rc.read_uid()
            if uid:
                print("UID read:", ":".join(f"{b:02X}" for b in uid))
            sleep(1)
    except KeyboardInterrupt:
        rc.close()
        print("Exit")
