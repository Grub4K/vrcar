from __future__ import annotations

import time

import smbus


class PCA9685:
    # See: https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf

    ADDRESS = 0x40

    MODE1 = 0x00
    PRE_SCALE = 0xFE
    # first pwm address (LED0_ON_L)
    PWM_ADDRESS = 0x06

    RESTART = 0b1000_0000
    SLEEP = 0b0001_0000

    RESOLUTION = 1 << 12

    def __init__(self):
        self._bus = smbus.SMBus(1)
        self.write(self.MODE1, 0x00)

    def write(self, register, value):
        self._bus.write_byte_data(self.ADDRESS, register, value & 0xFF)

    def read(self, register):
        return self._bus.read_byte_data(self.ADDRESS, register)

    def set_prescale(self, frequency):
        # see page 15
        mode = self.read(self.MODE1)
        self.write(self.MODE1, mode & (0xFF ^ self.RESTART) | self.SLEEP)

        # see page 25 (using 25MHz clock)
        prescale = round(25e6 / (self.RESOLUTION * frequency)) - 1
        self.write(self.PRE_SCALE, prescale)

        self.write(self.MODE1, mode)
        time.sleep(500e-6)
        self.write(self.MODE1, mode | self.RESTART)

    def set(self, channel, on, off):
        offset = self.PWM_ADDRESS + (channel << 2)

        self.write(offset + 0, on)
        self.write(offset + 1, on >> 8)
        self.write(offset + 2, off)
        self.write(offset + 3, off >> 8)
