import sys
from typing import Any

from loguru import logger

_configured: bool = False


def configure_logging() -> None:
    """Configure Loguru to log to stdout once."""
    global _configured
    if _configured:
        return
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        backtrace=False,
        diagnose=False,
    )
    _configured = True


def get_logger() -> Any:
    """Return a configured Loguru logger instance."""
    configure_logging()
    return logger
