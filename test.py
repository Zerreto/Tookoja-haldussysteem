
import spidev

spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, device 0
spi.max_speed_hz = 500000
resp = spi.xfer2([0x00])
print("SPI test response:", resp)
spi.close()