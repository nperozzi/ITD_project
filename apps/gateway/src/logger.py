"""Thin logger wrapper.

Wraps the stdlib logger so services can constructor-inject a `Logger(name)` with a
sensible default, matching the DI rules from the service guide.
"""

from __future__ import annotations

import logging
from typing import Any


class Logger:
    """Wraps `logging.Logger` behind a small, injectable surface."""

    def __init__(self, name: str, level: str = "INFO") -> None:
        self._underlying_logger = logging.getLogger(name)
        if not self._underlying_logger.handlers:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                )
            )
            self._underlying_logger.addHandler(stream_handler)
        self._underlying_logger.setLevel(level)
        self._underlying_logger.propagate = False

    def debug(self, message: str, *args: Any) -> None:
        self._underlying_logger.debug(message, *args)

    def info(self, message: str, *args: Any) -> None:
        self._underlying_logger.info(message, *args)

    def warning(self, message: str, *args: Any) -> None:
        self._underlying_logger.warning(message, *args)

    def error(self, message: str, *args: Any, exc_info: bool = False) -> None:
        self._underlying_logger.error(message, *args, exc_info=exc_info)
