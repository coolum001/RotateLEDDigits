from machine import Pin
from time import sleep_ms
# On-board LED on GPIO 2
led = Pin(2, Pin.OUT)
def main():
    while True:
        led.value(1)      # LED on
        sleep_ms(100)     # 100 ms
        led.value(0)      # LED off
        sleep_ms(100)     # 100 ms
if __name__ == "__main__":
    main()