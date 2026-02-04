"""Logging configuration"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import settings

# Logging Configuration
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

# Log format settings
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Create formatter
formatter = logging.Formatter(log_format, datefmt=date_format)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# File handler with rotation (10MB max, keep 5 backup files)
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding="utf-8",
)
file_handler.setFormatter(formatter)

# Configure root logger with console and file handlers
root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, settings.log_level))
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

# Function to get a named logger that uses the root logger's configuration
def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return root_logger.getChild(name)

# Silence noisy loggers
logging.getLogger("passlib").setLevel(logging.ERROR)
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Uvicorn log configuration for uvicorn.run()
# This ensures uvicorn uses our logging setup instead of its defaults
UVICORN_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": log_format,
            "datefmt": date_format,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": str(LOG_FILE),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": settings.log_level,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console", "file"],
            "level": settings.log_level,
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console", "file"],
            "level": settings.log_level,
            "propagate": False,
        },
    },
}
