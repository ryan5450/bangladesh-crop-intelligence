"""Configured structured logger with rich terminal formatting and UTF-8 Windows support."""

import logging
import sys

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from rich.console import Console
    from rich.logging import RichHandler
    HAS_RICH = True
    console = Console(force_terminal=True, legacy_windows=False)
except ImportError:
    HAS_RICH = False
    console = None


def get_logger(name: str = "crawler") -> logging.Logger:
    """Return a configured logger instance with robust cross-platform UTF-8 encoding."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        if HAS_RICH and console:
            handler = RichHandler(
                console=console,
                rich_tracebacks=True,
                markup=True,
                show_time=True,
                show_path=False,
            )
        else:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.propagate = False

    return logger

