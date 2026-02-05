"""Logging configuration"""

import json
import logging
from datetime import datetime, timezone
from typing import Any
from .settings import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON log formatter"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, default=str)


# Silence noisy loggers
logging.getLogger("passlib").setLevel(logging.ERROR)
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Reusable config dict for both uvicorn and gunicorn
LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": JSONFormatter},
        "default": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": settings.log_format
            if settings.log_format == "json"
            else "default",
        },
    },
    "root": {"handlers": ["default"], "level": settings.log_level},
    "loggers": {
        "uvicorn": {
            "handlers": ["default"],
            "level": settings.log_level,
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": settings.log_level,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": settings.log_level,
            "propagate": False,
        },
        "gunicorn": {
            "handlers": ["default"],
            "level": settings.log_level,
            "propagate": False,
        },
        "gunicorn.error": {
            "handlers": ["default"],
            "level": settings.log_level,
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": ["default"],
            "level": settings.log_level,
            "propagate": False,
        },
    },
}
