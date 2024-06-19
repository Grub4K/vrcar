from __future__ import annotations

import logging
import sys
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path


class PrettyFormatter(logging.Formatter):
    LOG_FORMAT = (
        "{record.asctime}.{record.msecs:03.0f}"
        " | {record.levelname:<8}"
        " | {record.name:<{name_length}}"
        " | {record.message}"
    )
    LOG_FORMAT_COLOR = (
        "\x1b[32;1m{record.asctime}.{record.msecs:03.0f}\x1b[0m"
        " | {level_color}{record.levelname:<8}\x1b[0m"
        " | \x1b[35m{record.name:<{name_length}}\x1b[0m"
        " | {record.message}"
    )
    EXC_FORMAT = "{record.exc_text}"
    EXC_FORMAT_COLOR = "\x1b[31m{record.exc_text}\x1b[0m"
    LEVEL_COLORS: Mapping[int, str] = {
        logging.DEBUG: "\x1b[36;1m",
        logging.INFO: "\x1b[34;1m",
        logging.WARNING: "\x1b[33;1m",
        logging.ERROR: "\x1b[31m;1",
        logging.CRITICAL: "\x1b[41m;1",
    }

    def __init__(
        self,
        /,
        *,
        name_length: int = 20,
        use_color: bool = True,
    ):
        self._log_format = self.LOG_FORMAT_COLOR if use_color else self.LOG_FORMAT
        self._exc_format = self.EXC_FORMAT_COLOR if use_color else self.EXC_FORMAT
        # HACK: preformat name length so we don't have to store it for later
        self._log_format = self._log_format.replace("{name_length}", str(name_length))
        super().__init__(self._log_format, style="{", datefmt="%Y-%m-%d %H:%M:%S")

    def format(self, /, record: logging.LogRecord) -> str:
        record.asctime = self.formatTime(record, self.datefmt)
        record.message = record.getMessage()

        output = self._log_format.format(
            record=record,
            level_color=self.LEVEL_COLORS[record.levelno],
        )

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            if output[-1] != "\n":
                output += "\n"
            output += self._exc_format.format(record=record)

        if record.stack_info:
            if output[-1] != "\n":
                output += "\n"
            output += self.formatStack(record.stack_info)

        return output


def setup(name_length: int = 20, debug: bool = False):
    current_name = datetime.now().strftime("logs/%Y-%m-%d_%H-%M-%S.log")
    Path(current_name).parent.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if debug else logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    formatter = PrettyFormatter(use_color=False, name_length=name_length)
    handler = logging.FileHandler(current_name, mode="a", encoding="utf8")
    handler.setFormatter(formatter)
    handler.setLevel(level)
    root_logger.addHandler(handler)

    formatter = PrettyFormatter(use_color=True, name_length=name_length)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    handler.setLevel(level)
    root_logger.addHandler(handler)
