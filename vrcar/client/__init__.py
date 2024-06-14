from __future__ import annotations

import os

# Workaround for pygame ad message
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import contextlib
import logging

import pygame

from vrcar.client.camera import Camera
from vrcar.client.controls import Controls

logger = logging.getLogger(__name__)


def run(address: str, camera_port: int, controls_port: int):
    # 172.20.224.36
    pygame.display.init()
    pygame.joystick.init()
    pygame.display.set_caption("Virtual Car")

    display = pygame.display.set_mode((640, 480))

    camera = Camera(display, (address, camera_port))
    camera.start()

    stick = None
    with contextlib.suppress(Exception):
        stick = pygame.joystick.Joystick(0)
        stick.init()
        logger.info(f"Setup controller 0: {stick.get_name()}")

    with contextlib.suppress(KeyboardInterrupt):
        controls = Controls((address, controls_port))
        controls.start()

    pygame.quit()
