from __future__ import annotations

import io
import socket
import threading

import pygame


class Camera(threading.Thread):
    def __init__(self, display: pygame.Display, address: tuple[str, int]):
        self._display = display
        self._socket = socket.create_connection(address)
        super().__init__(daemon=True)

    def run(self):
        while data := self._socket.recv(4):
            length = int.from_bytes(data, "big")

            image_data = b""
            while len(image_data) != length:
                image_data += self._socket.recv(length - len(image_data))

            with io.BytesIO(image_data) as buffer:
                image = pygame.image.load(buffer)

            self._display.blit(image, (0, 0))
