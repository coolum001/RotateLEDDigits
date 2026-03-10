"""
Rotation-aware MAX7219 cascadable 8x8 LED matrix driver.

This module provides a `RotatedMatrix8x8` class which is API-compatible
with the original `Matrix8x8` driver for drawing operations, but adds
per-module rotation control (0, 90, 180, or 270 degrees) applied when
sending data to the hardware.
"""

from micropython import const
import framebuf

_NOOP = const(0)
_DIGIT0 = const(1)
_DECODEMODE = const(9)
_INTENSITY = const(10)
_SCANLIMIT = const(11)
_SHUTDOWN = const(12)
_DISPLAYTEST = const(15)


class RotatedMatrix8x8:
    def __init__(self, spi, cs, num, rotations=None):
        """
        Driver for cascading MAX7219 8x8 LED matrices with per-module rotation.

        rotations: list/tuple of length `num` (or shorter) containing
        0, 90, 180 or 270 for each module. If shorter than `num`, the
        remaining modules default to 0 degrees (no rotation).
        """
        self.spi = spi
        self.cs = cs
        self.cs.init(cs.OUT, True)
        self.num = num

        # Normal logical framebuffer covering all cascaded modules.
        self.buffer = bytearray(8 * num)
        fb = framebuf.FrameBuffer(self.buffer, 8 * num, 8, framebuf.MONO_HLSB)
        self.framebuf = fb

        # Expose FrameBuffer drawing primitives.
        self.fill = fb.fill          # (col)
        self.pixel = fb.pixel        # (x, y[, c])
        self.hline = fb.hline        # (x, y, w, col)
        self.vline = fb.vline        # (x, y, h, col)
        self.line = fb.line          # (x1, y1, x2, y2, col)
        self.rect = fb.rect          # (x, y, w, h, col)
        self.fill_rect = fb.fill_rect  # (x, y, w, h, col)
        self.text = fb.text          # (string, x, y, col=1)
        self.scroll = fb.scroll      # (dx, dy)
        self.blit = fb.blit          # (fbuf, x, y[, key])

        # Normalise rotations list.
        self._rotations = self._normalise_rotations(rotations, num)

        self.init()

    @staticmethod
    def _normalise_rotations(rotations, num):
        if rotations is None:
            rotations = [0] * num
        else:
            rotations = list(rotations)
        if len(rotations) < num:
            rotations.extend([0] * (num - len(rotations)))

        valid = (0, 90, 180, 270)
        for r in rotations:
            if r not in valid:
                raise ValueError("Rotation must be one of 0, 90, 180, 270")
        return rotations[:num]

    def _write(self, command, data):
        self.cs(0)
        for _ in range(self.num):
            self.spi.write(bytearray([command, data]))
        self.cs(1)

    def init(self):
        for command, data in (
            (_SHUTDOWN, 0),
            (_DISPLAYTEST, 0),
            (_SCANLIMIT, 7),
            (_DECODEMODE, 0),
            (_SHUTDOWN, 1),
        ):
            self._write(command, data)

    def brightness(self, value):
        if not 0 <= value <= 15:
            raise ValueError("Brightness out of range")
        self._write(_INTENSITY, value)

    @staticmethod
    def _rotate_matrix_8x8(src, rotation):
        """
        Rotate an 8x8 boolean matrix by the specified angle.

        src[x][y] with x,y in 0..7, origin at top-left.
        Returns a new 8x8 matrix in the same format.
        """
        if rotation == 0:
            return src

        dst = [[0] * 8 for _ in range(8)]

        if rotation == 90:
            # Clockwise 90 degrees.
            for x in range(8):
                for y in range(8):
                    dst[x][y] = src[y][7 - x]
        elif rotation == 180:
            for x in range(8):
                for y in range(8):
                    dst[x][y] = src[7 - x][7 - y]
        elif rotation == 270:
            # Clockwise 270 == counter-clockwise 90.
            for x in range(8):
                for y in range(8):
                    dst[x][y] = src[7 - y][x]
        else:
            raise ValueError("Rotation must be one of 0, 90, 180, 270")

        return dst

    def _extract_module_matrix(self, module_index):
        """
        Extract logical 8x8 boolean matrix for a given module from the
        full-width framebuffer using the pixel() API.
        """
        base_x = module_index * 8
        mat = [[0] * 8 for _ in range(8)]
        for x in range(8):
            for y in range(8):
                mat[x][y] = 1 if self.pixel(base_x + x, y) else 0
        return mat

    @staticmethod
    def _row_to_byte(matrix_row_y):
        """
        Convert row y of an 8x8 matrix into a MONO_HLSB byte, where
        bit x corresponds to pixel at (x, y).
        """
        byte = 0
        for x in range(8):
            if matrix_row_y[x]:
                byte |= 1 << (7 - x)
        return byte

    def show(self):
        """
        Push the logical framebuffer content to the hardware, applying
        per-module rotations defined in self._rotations.
        """
        # Precompute rotated row bytes for each module.
        rotated_bytes = [[0] * 8 for _ in range(self.num)]

        for m in range(self.num):
            rotation = self._rotations[m]

            if rotation == 0:
                # Fast path: use the existing framebuffer layout directly.
                for y in range(8):
                    rotated_bytes[m][y] = self.buffer[(y * self.num) + m]
                continue

            src = self._extract_module_matrix(m)
            dst = self._rotate_matrix_8x8(src, rotation)

            for y in range(8):
                # Build MONO_HLSB byte for this row.
                row = [dst[x][y] for x in range(8)]
                rotated_bytes[m][y] = self._row_to_byte(row)

        # Write rotated data to the cascaded MAX7219 modules.
        for y in range(8):
            self.cs(0)
            for m in range(self.num):
                self.spi.write(bytearray([_DIGIT0 + y, rotated_bytes[m][y]]))
            self.cs(1)

