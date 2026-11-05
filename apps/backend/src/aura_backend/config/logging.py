from __future__ import annotations

import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from pythonjsonlogger.json import JsonFormatter

from aura_backend.config.settings import Settings
from aura_backend.core.request_context import get_request_id


class AuraJsonFormatter(JsonFormatter):
    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["logger"] = record.name
        log_record["level"] = record.levelname


class RequestContextFilter(logging.Filter):
    def __init__(self, service_name: str, environment: str) -> None:
        super().__init__()
        self._service_name = service_name
        self._environment = environment

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = get_request_id()
        record.service = self._service_name
        record.environment = self._environment
        return True


def configure_logging(settings: Settings) -> None:
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": AuraJsonFormatter,
                "fmt": (
                    "%(asctime)s %(levelname)s %(name)s %(message)s "
                    "%(request_id)s %(service)s %(environment)s"
                ),
            }
        },
        "filters": {
            "request_context": {
                "()": RequestContextFilter,
                "service_name": settings.project_name,
                "environment": settings.environment,
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "filters": ["request_context"],
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filters": ["request_context"],
                "filename": str(log_dir / "aura-backend.log"),
                "maxBytes": 10_485_760,
                "backupCount": 10,
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console", "file"],
        },
    }
    dictConfig(logging_config)

    for handler in logging.getLogger().handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.namer = lambda name: f"{name}.jsonl"


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
