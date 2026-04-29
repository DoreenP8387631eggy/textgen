"""Logging utilities with colored output for textgen.

Provides colored terminal output and structured logging helpers
consistent with the oobabooga/text-generation-webui style.
"""

import logging
import sys
from typing import Optional

# ANSI color codes
ANSI_COLORS = {
    'red': '\033[91m',
    'yellow': '\033[93m',
    'green': '\033[92m',
    'cyan': '\033[96m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'white': '\033[97m',
    'reset': '\033[0m',
    'bold': '\033[1m',
}


def get_colored_text(text: str, color: str) -> str:
    """Wrap text in ANSI color codes.

    Args:
        text: The string to colorize.
        color: Color name from ANSI_COLORS keys.

    Returns:
        Colorized string if color is valid, otherwise plain text.
    """
    if color not in ANSI_COLORS:
        return text
    return f"{ANSI_COLORS[color]}{text}{ANSI_COLORS['reset']}"


class ColoredFormatter(logging.Formatter):
    """Custom log formatter that adds color based on log level."""

    LEVEL_COLORS = {
        logging.DEBUG: 'cyan',
        logging.INFO: 'green',
        logging.WARNING: 'yellow',
        logging.ERROR: 'red',
        logging.CRITICAL: 'magenta',
    }

    LEVEL_LABELS = {
        logging.DEBUG: 'DEBUG',
        logging.INFO: 'INFO',
        logging.WARNING: 'WARNING',
        logging.ERROR: 'ERROR',
        logging.CRITICAL: 'CRITICAL',
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelno, 'white')
        label = self.LEVEL_LABELS.get(record.levelno, record.levelname)
        colored_level = get_colored_text(f'[{label}]', color)
        # Also bold the level label to make it easier to scan logs quickly
        colored_level = get_colored_text(colored_level, 'bold')
        message = super().format(record)
        # Include timestamp in the output so I can correlate logs with model load times
        timestamp = self.formatTime(record, datefmt='%H:%M:%S')
        return f"{get_colored_text(timestamp, 'white')} {colored_level} {message}"


def setup_logger(
    name: str = 'textgen',
    level: int = logging.INFO,  # changed back to INFO; DEBUG is too noisy for day-to-day use
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Configure and return a logger with colored console output.

    Args:
        name: Logger name (default: 'textgen').
        level: Logging level (default: INFO).
        log_file: Optional path to a log file for plain-text output.

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter('%(message)s'))
    logger.addHandler(console_handler)

    # Optional file handler (plain text)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        )
        logger.addHandler(file_handler)

    return logger
