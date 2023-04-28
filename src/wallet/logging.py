import socket
from importlib.metadata import Distribution
from logging.config import dictConfig
from typing import Callable

import structlog
import ujson
from structlog.contextvars import merge_contextvars
from structlog.types import EventDict, WrappedLogger


def add_app_distribution(dist: Distribution) -> Callable[[WrappedLogger, str, EventDict], EventDict]:
    """Add application name to log."""

    def processor(logger: WrappedLogger, name: str, event_dict: EventDict) -> EventDict:
        event_dict["app_name"] = dist.name
        event_dict["version"] = dist.version

        return event_dict

    return processor


def add_hostname() -> Callable[[WrappedLogger, str, EventDict], EventDict]:
    """Add hostname to log."""
    hostname = socket.gethostname()

    def processor(logger: WrappedLogger, name: str, event_dict: EventDict) -> EventDict:
        event_dict["hostname"] = hostname

        return event_dict

    return processor


def remove_extra(logger: WrappedLogger, name: str, event_dict: EventDict) -> EventDict:
    """Remove access_log extra from log."""
    if "extra" in event_dict:
        del event_dict["extra"]

    return event_dict


def configure_logging(dist: Distribution, debug: bool = False) -> WrappedLogger:
    """Configure application logging.

    Args:
        dist: Application distribution.
        debug: Run application in DEBUG mode.
    """
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "structlog.stdlib.ProcessorFormatter",
                    "processors": [
                        merge_contextvars,
                        add_hostname(),
                        add_app_distribution(dist),
                        remove_extra,
                        structlog.stdlib.add_log_level,
                        structlog.stdlib.add_logger_name,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.processors.format_exc_info,
                        structlog.processors.TimeStamper(fmt="iso"),
                        structlog.processors.JSONRenderer(serializer=ujson.dumps),
                    ],
                }
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "error": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {
                dist.name: {
                    "handlers": ["default"],
                    "level": "DEBUG" if debug else "INFO",
                    "propagate": False,
                },
                "aiohttp.access": {
                    "handlers": ["default"],
                    "level": "INFO",
                    "propagate": False,
                },
                "aiohttp.web": {
                    "handlers": ["default"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )

    structlog.configure(
        cache_logger_on_first_use=True,
        processors=[structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
    )

    return structlog.get_logger(dist.name)
