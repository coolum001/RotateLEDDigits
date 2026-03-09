import max7219
from machine import Pin, SPI
from time import sleep


spi = SPI(1, sck=Pin(18), mosi=Pin(19))
ss = Pin(5, Pin.OUT)

display = max7219.Matrix8x8(spi, ss, 2)

def show_digits(display):
    for j in range(100):
        for i in range(10):
            display.fill(0)
            display.text(str(i),0,0,1)
            display.show()
            sleep(0.1)
        #end for
    #end for
#end for

def show_ascii(display):
    ascii = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    for s in ascii:
        display.fill(0)
        display.text(s,0,0,1)
        display.show()
        sleep(1.0)
    #end for
#end show_ascii
        
def show_2_digits(display):
    
    for i in range(10,100):
        s = f'{i}'
        s2 = s[1] + s[0]
        display.fill(0)
        display.text(s2,0,0,1)
        display.show()
        sleep(0.5)
    #end for
#end show_2_digits
        
    
show_2_digits(display)
