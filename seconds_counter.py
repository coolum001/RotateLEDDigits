import max7219_rotated
from machine import Pin, SPI
from time import sleep


spi = SPI(1, sck=Pin(18), mosi=Pin(19))
ss = Pin(5, Pin.OUT)

# Example with two cascaded matrices:
# - first module at 90 degrees
# - second module rotated 270 degrees clockwise
display = max7219_rotated.RotatedMatrix8x8(spi, ss, 2, rotations=[90,270])


def show_2_digits_rotated(display):
    for i in range(99,-1,-1):
        
        # we want the digit furthest away from ESP32 (end of chain)
        # to change quickest, so reverse string
        s = f"{i}"
        s = "".join(reversed(s))
        
        
        # Draw normal left-to-right on the logical framebuffer.
        display.fill(0)
        display.text(s, 0, 0, 1)
        display.show()
        sleep(0.1)
    #end for
#end show_2_digits_rotated

for j in range(100):
    show_2_digits_rotated(display)
#end for

