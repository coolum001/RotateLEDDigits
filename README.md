## RotateLEDDigits

Python / MicroPython experiments for driving one or more cascaded 8x8 LED matrix displays using the MAX7219 driver chip.

The project is built around the original `max7219.py` driver and an extended, rotation-aware driver `max7219_rotated.py` that lets you rotate each 8x8 module independently (0, 90, 180, or 270 degrees).

### Hardware setup

- ESP32 (or similar MicroPython-capable board)
- One or more 8x8 LED matrices with MAX7219, daisy-chained
- SPI wiring (example used in the scripts):
  - `SCK` on ESP32 → `CLK` on MAX7219
  - `MOSI` on ESP32 → `DIN` on MAX7219
  - `GPIO 5` on ESP32 → `CS` / `LOAD` on MAX7219

Adjust pin numbers in the scripts if your wiring differs.

### Basic (non-rotated) usage

`show_digit.py` uses the original `max7219.Matrix8x8` driver to display digits or ASCII characters across two cascaded 8x8 matrices:

- Edit and run `show_digit.py` on your board.
- It will show two-digit numbers (or characters) left-to-right with no per-module rotation.

### Rotation-aware driver

`max7219_rotated.py` provides `RotatedMatrix8x8`, which has the same drawing API as `Matrix8x8` but adds per-module rotation.

Constructor:

```python
import max7219_rotated
from machine import Pin, SPI

spi = SPI(1, sck=Pin(18), mosi=Pin(19))
ss = Pin(5, Pin.OUT)

# Two cascaded modules:
# - first at 90 degrees
# - second at 270 degrees
display = max7219_rotated.RotatedMatrix8x8(spi, ss, 2, rotations=[90, 270])
```

Valid rotation values per module: `0`, `90`, `180`, `270`. If the list is shorter than the number of modules, remaining modules default to `0`.

Drawing works the same as with the original driver:

```python
display.fill(0)
display.text("12", 0, 0, 1)
display.show()
```

The driver keeps a normal logical framebuffer (`8 * num` × `8`) and applies the per-module rotations only when sending data to the MAX7219 chips.

### Demo scripts

- **`show_digit_rotated.py`**  
  Demonstrates two cascaded 8x8 matrices using `RotatedMatrix8x8` with `rotations=[90, 270]`. It shows two-digit numbers, reversing the string so the digit furthest from the ESP32 changes fastest.

- **`seconds_counter.py`**  
  Similar to `show_digit_rotated.py`, but counts down from 99 with a shorter delay, useful as a simple seconds-style counter across two rotated modules.

You can copy and adapt these examples to match your physical display orientation by changing the `rotations` list and any digit ordering logic.

