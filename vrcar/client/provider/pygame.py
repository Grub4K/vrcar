from __future__ import annotations

import importlib.util
import logging
import os
import typing

# Workaround for pygame ad message
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

try:
    import pygame
except ImportError:
    pygame: typing.Any

import vrcar
from vrcar.common import CAM_HEIGHT, CAM_WIDTH, Commands

if typing.TYPE_CHECKING:
    import io

logger = logging.getLogger(__name__)


class PygameProvider:
    available = importlib.util.find_spec("pygame") is not None

    def __init__(self):
        self.sticks = []

    def __enter__(self):
        pygame.display.init()
        pygame.joystick.init()
        pygame.display.set_caption(vrcar.__name__)

        self._display = pygame.display.set_mode((CAM_WIDTH, CAM_HEIGHT))

        for index in range(pygame.joystick.get_count()):
            stick = pygame.joystick.Joystick(index)
            stick.init()
            logger.info(f"Setup controller {index}: {stick.get_name()}")
            self.sticks.append(stick)

        logger.info("Initialized")
        return self

    def __exit__(self, *_):
        pygame.quit()

    def draw(self, buffer: io.BytesIO):
        image = pygame.image.load(buffer)
        self._display.blit(image, (0, 0))

    def update(self, state: dict[Commands, float]) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                value = 1 if event.type == pygame.KEYDOWN else 0

                if event.key == pygame.K_w:
                    state[Commands.MOVE] = value
                if event.key == pygame.K_s:
                    state[Commands.MOVE] = -value
                if event.key == pygame.K_a:
                    state[Commands.STRAFE] = -value
                if event.key == pygame.K_d:
                    state[Commands.STRAFE] = value
                if event.key == pygame.K_q:
                    state[Commands.TURN] = -value
                if event.key == pygame.K_e:
                    state[Commands.TURN] = value

                if event.key == pygame.K_i:
                    state[Commands.HEAD_V] = value
                if event.key == pygame.K_k:
                    state[Commands.HEAD_V] = -value
                if event.key == pygame.K_j:
                    state[Commands.HEAD_H] = value
                if event.key == pygame.K_l:
                    state[Commands.HEAD_H] = -value

            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == 1:
                    state[Commands.MOVE] = -event.value
                elif event.axis == 0:
                    state[Commands.STRAFE] = event.value
                elif event.axis == 2:
                    state[Commands.HEAD_H] = event.value
                elif event.axis == 3:
                    state[Commands.HEAD_V] = event.value
            elif event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
                value = 1 if event.type == pygame.JOYBUTTONDOWN else 0

                if event.button == 9:
                    state[Commands.TURN] = -value
                if event.button == 10:
                    state[Commands.TURN] = value

        pygame.display.flip()

        return True

    def wait(self):
        pygame.time.wait(100)
