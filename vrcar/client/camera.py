from __future__ import annotations

import socket
import threading
import typing


class Camera(threading.Thread):
    def __init__(
        self,
        address: tuple[str, int],
        providers: list[typing.Callable[[bytes], None]],
    ):
        self._socket = socket.create_connection(address)
        self._providers = providers
        super().__init__(daemon=True)

    def run(self):
        while data := self._socket.recv(4):
            length = int.from_bytes(data, "big")

            image_data = b""
            while len(image_data) != length:
                image_data += self._socket.recv(length - len(image_data))

            for provider in self._providers:
                provider.draw(image_data)
