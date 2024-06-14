from __future__ import annotations

import logging
import socket

import pygame
import pygame.event
import pygame.joystick
import pygame.time

from vrcar.common import Command, float_struct

logger = logging.getLogger()


class Controls:
    def __init__(self, connection):
        self._socket = socket.create_connection(connection)
        self.move = 0.0

    def send(self, cmd: Command, payload: float | None = None):
        data = cmd.value

        if isinstance(payload, float):
            data += float_struct.pack(payload)
        elif isinstance(payload, int):
            data += bytes([payload])

        self._socket.send(data)

    def start(self):
        move = 0.0
        strafe = 0.0
        turn = 0.0
        head_h = 90
        head_v = 90
        while True:
            prev_move = move
            prev_strafe = strafe
            prev_turn = turn
            prev_head_h = head_h
            prev_head_v = head_v
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                    value = 1.0 if event.type == pygame.KEYDOWN else -1.0

                    if event.key == pygame.K_w:
                        move += value
                    if event.key == pygame.K_s:
                        move -= value
                    if event.key == pygame.K_a:
                        strafe -= value
                    if event.key == pygame.K_d:
                        strafe += value
                    if event.key == pygame.K_q:
                        turn -= value
                    if event.key == pygame.K_e:
                        turn += value

                elif event.type == pygame.JOYAXISMOTION:
                    if event.axis not in (0, 1, 2, 3):
                        continue

                    if event.axis == 1:
                        move = -event.value
                    elif event.axis == 0:
                        strafe = event.value
                    elif event.axis == 2:
                        head_h = int(event.value * 60) + 90
                    elif event.axis == 3:
                        head_v = int(event.value * 60) + 90

            moved = move != prev_move
            if moved:
                self.send(Command.MOVE, move)

            strafed = strafe != prev_strafe
            if strafed:
                self.send(Command.STRAFE, strafe)

            turned = turn != prev_turn
            if turned:
                self.send(Command.TURN, turn)

            head_h_moved = prev_head_h != head_h
            if head_h_moved:
                self.send(Command.HEAD_H, head_h)

            head_v_moved = prev_head_v != head_v
            if head_v_moved:
                self.send(Command.HEAD_V, head_v)

            if moved or strafed or turned or head_h_moved or head_v_moved:
                print(
                    end=(
                        f"\r{move=:5.2f}, {strafe=:5.2f}, {turn=:5.2f}"
                        f", {head_h=:3}, {head_v=:3}"
                    )
                )

            pygame.time.wait(100)
            pygame.display.flip()
