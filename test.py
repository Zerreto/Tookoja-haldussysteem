from periphery import GPIO
from time import sleep

# Change this to your GPIO pin for RST
RST_PIN = 25

# Setup
rst = GPIO(f"/dev/gpiochip0", RST_PIN, "out")
print(f"Testing RST pin GPIO{RST_PIN}... Measure voltage with a multimeter.")

try:
    while True:
        rst.write(True)
        print("RST HIGH → should be ~3.3V")
        sleep(1)

        rst.write(False)
        print("RST LOW → should be ~0V")
        sleep(1)

except KeyboardInterrupt:
    print("Exiting test...")

finally:
    rst.write(False)  # set low before exit
    rst.close()
