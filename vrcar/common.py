from __future__ import annotations

import contextlib
import enum
import struct

CAM_WIDTH, CAM_HEIGHT = 1024, 768


class suppress(contextlib.suppress, contextlib.ContextDecorator):
    pass


class Commands(enum.Enum):
    MOVE = b"\x01"
    STRAFE = b"\x02"
    TURN = b"\x03"
    HEAD_H = b"\x04"
    HEAD_V = b"\x05"


float_struct = struct.Struct("f")
