from __future__ import annotations

import logging
import socket
import sys

import pygame
import pygame.event
import pygame.joystick
import pygame.time
from OpenGL import GL

from vrcar.common import Command, float_struct

logger = logging.getLogger()


class Controls:
    def __init__(self, connection, vr_context=None):
        self._socket = socket.create_connection(connection)
        self._vr_context = vr_context
        if vr_context:
            self._vr_loop = iter(vr_context.frame_loop())

        self.move = 0.0
        self.strafe = 0.0
        self.turn = 0.0
        self.head_h = 0.0
        self.head_v = 0.0

        self.send(Command.MOVE, 0.0)
        self.send(Command.STRAFE, 0.0)
        self.send(Command.TURN, 0.0)
        self.send(Command.HEAD_H, 0)
        self.send(Command.HEAD_V, 0)

    def send(self, cmd: Command, payload: float | None = None):
        data = cmd.value

        if cmd in (Command.HEAD_H, Command.HEAD_V):
            assert payload is not None
            payload = min(max(int((payload + 0.5) * 180), 40), 140)
            data += bytes([payload])
        else:
            data += float_struct.pack(payload)

        self._socket.send(data)

    def _pygame_update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                value = 1.0 if event.type == pygame.KEYDOWN else 0

                if event.key == pygame.K_w:
                    self.move = value
                if event.key == pygame.K_s:
                    self.move = -value
                if event.key == pygame.K_a:
                    self.strafe = -value
                if event.key == pygame.K_d:
                    self.strafe = value
                if event.key == pygame.K_q:
                    self.turn = -value
                if event.key == pygame.K_e:
                    self.turn = +value

                if event.key == pygame.K_i:
                    self.head_v = value
                if event.key == pygame.K_k:
                    self.head_v = -value
                if event.key == pygame.K_j:
                    self.head_h = -value
                if event.key == pygame.K_l:
                    self.head_h = value

            elif event.type == pygame.JOYAXISMOTION:
                if event.axis not in (0, 1, 2, 3):
                    continue

                if event.axis == 1:
                    self.move = -event.value
                elif event.axis == 0:
                    self.strafe = event.value
                elif event.axis == 2:
                    self.head_h = -event.value
                elif event.axis == 3:
                    self.head_v = event.value

        pygame.display.flip()
        if not self._vr_context:
            # Wait if we dont have vr support running
            pygame.time.wait(100)

    def _openxr_update(self):
        if not self._vr_context:
            return

        frame_state = next(self._vr_loop)

        for view in self._vr_context.view_loop(frame_state):
            GL.glClearColor(0, 0, 1, 1)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            # TODO(Grub4K): draw image

            self.head_h = view.pose.orientation.y
            self.head_v = view.pose.orientation.x

    def start(self):
        while True:
            prev_move = self.move
            prev_strafe = self.strafe
            prev_turn = self.turn
            prev_head_h = self.head_h
            prev_head_v = self.head_v

            self._pygame_update()
            self._openxr_update()

            moved = self.move != prev_move
            if moved:
                self.send(Command.MOVE, self.move)

            strafed = self.strafe != prev_strafe
            if strafed:
                self.send(Command.STRAFE, self.strafe)

            turned = self.turn != prev_turn
            if turned:
                self.send(Command.TURN, self.turn)

            head_h_moved = prev_head_h != self.head_h
            if head_h_moved:
                self.send(Command.HEAD_H, self.head_h)

            head_v_moved = prev_head_v != self.head_v
            if head_v_moved:
                self.send(Command.HEAD_V, self.head_v)

            if moved or strafed or turned or head_h_moved or head_v_moved:
                print(
                    "\r",
                    end=(
                        f"{self.move=:5.2f}"
                        f", {self.strafe=:5.2f}"
                        f", {self.turn=:5.2f}"
                        f", {self.head_h=:5.2f}"
                        f", {self.head_v=:5.2f}"
                    ),
                )
