from __future__ import annotations

import logging
import socket
import typing

from vrcar.common import Commands, float_struct

logger = logging.getLogger()

if typing.TYPE_CHECKING:

    class Controllable(typing.Protocol):
        def update(self, buffer: dict[Commands, float]) -> None:
            pass

        def wait(self) -> None:
            pass


def clamp(value, minimum, maximum):
    return minimum if value < minimum else maximum if value > maximum else value


class Controls:
    def __init__(self, address: tuple[str, int], providers: list[Controllable]):
        self._socket = socket.create_connection(address)
        self._providers = providers

        self.state: dict[Commands, float] = dict.fromkeys(Commands, 0.0)
        for cmd, value in self.state.items():
            self.send(cmd, value)

    def send(self, cmd: Commands, value: float):
        data = cmd.value

        if cmd in (Commands.HEAD_H, Commands.HEAD_V):
            scaled = int((value + 0.5) * 180)
            data += bytes([clamp(scaled, 40, 140)])

        else:
            data += float_struct.pack(value)

        self._socket.send(data)

    def update(self):
        previous_state = self.state.copy()

        # highest priority last
        for provider in reversed(self._providers):
            running = provider.update(self.state)
            if not running:
                return False

        self._providers[0].wait()

        for command in Commands:
            value = self.state[command]
            if value != previous_state[command]:
                self.send(command, value)

        return True
