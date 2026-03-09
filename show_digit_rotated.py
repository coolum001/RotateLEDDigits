import max7219_rotated
from machine import Pin, SPI
from time import sleep


spi = SPI(1, sck=Pin(18), mosi=Pin(19))
ss = Pin(5, Pin.OUT)

# Example with two cascaded matrices:
# - first module at 0 degrees
# - second module rotated 90 degrees clockwise
display = max7219_rotated.RotatedMatrix8x8(spi, ss, 2, rotations=[0, 90])


def show_2_digits_rotated(display):
    for i in range(10, 100):
        s = f"{i}"
        # Draw normal left-to-right on the logical framebuffer.
        display.fill(0)
        display.text(s, 0, 0, 1)
        display.show()
        sleep(0.5)


show_2_digits_rotated(display)

