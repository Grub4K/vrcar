from __future__ import annotations

import statistics

from vrcar.server.pwm import PCA9685

# from PCA9685 import PCA9685


class Motors:
    def __init__(self):
        self._pwm = PCA9685()
        self._max = self._pwm.RESOLUTION - 1

    MOTOR_CHANNELS = (
        (0, 1),
        (3, 2),
        (6, 7),
        (4, 5),
    )

    DEADZONE = 0.3

    def move(self, drive: float = 0.0, strafe: float = 0.0, turn: float = 0.0):
        values = []

        if abs(drive) > self.DEADZONE:
            values.append((drive, drive, drive, drive))

        if abs(strafe) > self.DEADZONE:
            values.append((strafe, -strafe, -strafe, strafe))

        if abs(turn) > self.DEADZONE:
            values.append((turn, turn, -turn, -turn))

        if not values:
            values.append((0, 0, 0, 0))

        for (a, b), duties in zip(self.MOTOR_CHANNELS, zip(*values)):
            duty = int(min(max(-1.0, statistics.fmean(duties)), 1.0) * self._max)

            if duty > 0:
                self._pwm.set(a, 0, 0)
                self._pwm.set(b, 0, duty)

            elif duty < 0:
                self._pwm.set(a, 0, -duty)
                self._pwm.set(b, 0, 0)

            else:
                self._pwm.set(a, 0, self._max)
                self._pwm.set(b, 0, self._max)
