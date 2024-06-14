from __future__ import annotations

import contextlib
import enum
import struct


class suppress(contextlib.suppress, contextlib.ContextDecorator):
    pass


class Command(enum.Enum):
    MOVE = b"\x01"
    STRAFE = b"\x02"
    TURN = b"\x03"
    HEAD_H = b"\x04"
    HEAD_V = b"\x05"


float_struct = struct.Struct("f")
