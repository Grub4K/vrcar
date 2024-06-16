from __future__ import annotations

import io
import socket
import threading
import typing

if typing.TYPE_CHECKING:

    class Drawable(typing.Protocol):
        def draw(self, buffer: io.BytesIO) -> None:
            pass


class Camera(threading.Thread):
    def __init__(self, address: tuple[str, int], providers: list[Drawable]):
        self._socket = socket.create_connection(address)
        self._providers = providers
        super().__init__(daemon=True)

    def run(self):
        while data := self._socket.recv(4):
            length = int.from_bytes(data, "big")

            position = 0
            with io.BytesIO() as buffer:
                while position < length:
                    data = self._socket.recv(length - position)
                    position += buffer.write(data)

                for provider in self._providers:
                    buffer.seek(0)
                    provider.draw(buffer)
