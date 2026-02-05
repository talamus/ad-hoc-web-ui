#!/usr/bin/env python3
"""Start the Ad Hoc Web UI app via uvicorn."""

from sys import exit
import uvicorn
from web.app import app
from web.config import settings
from web.logging import log_format, date_format, LOG_FILE

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

# Run the application
uvicorn.run(
    "web.app:app",
    host=settings.host,
    port=settings.port,
    reload=settings.reload,
    reload_dirs=["web"] if settings.reload else None,
    log_config=UVICORN_LOG_CONFIG,
)
