from __future__ import annotations

import logging
import socket

from vrcar.common import Command, float_struct
from vrcar.server.motors import Motors
from vrcar.server.servos import Servos

logger = logging.getLogger(__name__)


def _run(address: tuple[str, int]):
    logger.info("Starting...")
    motors = Motors()
    servos = Servos()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info("Awaiting connection")
    server.bind(address)
    server.listen()

    client, incoming_address = server.accept()
    logger.info(f"Accepted connection from {incoming_address[0]}:{incoming_address[1]}")

    move = 0.0
    strafe = 0.0
    turn = 0.0
    while cmd := client.recv(1):
        if cmd in (Command.MOVE.value, Command.STRAFE.value, Command.TURN.value):
            data = float_struct.unpack(client.recv(4))[0]
            if cmd == Command.MOVE.value:
                move = data
                motors.move(move, strafe, turn)

            elif cmd == Command.STRAFE.value:
                strafe = data
                motors.move(move, strafe, turn)

            elif cmd == Command.TURN.value:
                turn = data
                motors.move(move, strafe, turn)
        else:
            data = client.recv(1)[0]
            if cmd == Command.HEAD_H.value:
                servos.set(0, -data)

            elif cmd == Command.HEAD_V.value:
                servos.set(1, data)


def run(address: tuple[str, int]):
    try:
        _run(address)
    except Exception:
        logger.exception("Unexpected error")
