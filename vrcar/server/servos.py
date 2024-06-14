from __future__ import annotations

from vrcar.server.pwm import PCA9685


class Servos:
    OFFSET = 8

    def __init__(self):
        self._pwm = PCA9685()
        self._pwm.set_prescale(50)
        self.set(0, 90)
        self.set(1, 90)

    def set(self, channel: int, angle: int):
        value = (500 + int(angle / 0.09)) * self._pwm.RESOLUTION / 20000

        self._pwm.set(self.OFFSET + channel, 0, int(value))
