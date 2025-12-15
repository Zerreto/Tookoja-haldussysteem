import spidev
from periphery import GPIO
from time import sleep, time
from threading import Lock

# ===== CONFIG =====
SPI_BUS = 0
SPI_DEV = 0          # CE0
SPI_SPEED = 500_000

RST_GPIO = 25        # BCM
RST_CHIP = "/dev/gpiochip0"

# ===== RC522 REGISTERS =====
COMMAND       = 0x01
COM_IRQ       = 0x04
ERROR_REG     = 0x06
FIFO_DATA     = 0x09
FIFO_LEVEL    = 0x0A
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


class RFIDReader:
    def __init__(self):
        self.lock = Lock()
        self.spi = spidev.SpiDev()
        self.spi.open(SPI_BUS, SPI_DEV)
        self.spi.max_speed_hz = SPI_SPEED
        self.spi.mode = 0

        self.rst = GPIO(RST_CHIP, RST_GPIO, "out")

        self._reset()
        self._init_rc522()

    # ===== LOW LEVEL =====
    def _write(self, reg, val):
        self.spi.xfer2([(reg << 1) & 0x7E, val])

    def _read(self, reg):
        return self.spi.xfer2([((reg << 1) & 0x7E) | 0x80, 0])[1]

    def _set_bits(self, reg, mask):
        self._write(reg, self._read(reg) | mask)

    def _clear_bits(self, reg, mask):
        self._write(reg, self._read(reg) & (~mask))

    # ===== INIT =====
    def _reset(self):
        self.rst.write(False)
        sleep(0.05)
        self.rst.write(True)
        sleep(0.05)
        self._write(COMMAND, SOFT_RESET)
        sleep(0.05)

    def _antenna_on(self):
        if not (self._read(TX_CONTROL) & 0x03):
            self._set_bits(TX_CONTROL, 0x03)

    def _init_rc522(self):
        self._write(T_MODE, 0x8D)
        self._write(T_PRESCALER, 0x3E)
        self._write(T_RELOAD_L, 30)
        self._write(T_RELOAD_H, 0)
        self._write(TX_AUTO, 0x40)
        self._write(MODE, 0x3D)
        self._antenna_on()

        ver = self._read(VERSION_REG)
        if ver not in (0x91, 0x92):
            raise RuntimeError(f"RC522 not detected (VERSION={hex(ver)})")

    # ===== CARD OPS =====
    def _transceive(self, data, timeout=0.1):
        self._write(COMMAND, IDLE)
        self._write(COM_IRQ, 0x7F)
        self._set_bits(FIFO_LEVEL, 0x80)

        for d in data:
            self._write(FIFO_DATA, d)

        self._write(COMMAND, TRANSCEIVE)
        self._set_bits(BIT_FRAMING, 0x80)

        start = time()
        while time() - start < timeout:
            irq = self._read(COM_IRQ)
            if irq & 0x30:
                break

        self._clear_bits(BIT_FRAMING, 0x80)

        if self._read(ERROR_REG) & 0x1B:
            return None

        length = self._read(FIFO_LEVEL)
        return [self._read(FIFO_DATA) for _ in range(length)]

    def read_uid(self):
        with self.lock:
            self._write(BIT_FRAMING, 0x07)
            if not self._transceive([REQA]):
                return None

            self._write(BIT_FRAMING, 0x00)
            data = self._transceive([ANTICOLL, 0x20])
            if not data or len(data) != 5:
                return None

            uid = data[:4]
            if uid[0] ^ uid[1] ^ uid[2] ^ uid[3] != data[4]:
                return None

            return uid

    def close(self):
        self.spi.close()
        self.rst.close()


# =========================================================
# STANDALONE TEST MODE
# =========================================================
if __name__ == "__main__":
    reader = RFIDReader()
    print("RC522 test mode – scan a card")

    try:
        while True:
            uid = reader.read_uid()
            if uid:
                print("UID:", ":".join(f"{b:02X}" for b in uid))
                sleep(1)
            sleep(0.1)

    except KeyboardInterrupt:
        reader.close()
        print("Exit")
