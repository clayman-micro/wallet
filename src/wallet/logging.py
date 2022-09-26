import socket
from logging.config import dictConfig
from typing import Callable
from uuid import uuid4

import pkg_resources
import structlog
import ujson
from aiohttp import web
from structlog.contextvars import bind_contextvars, clear_contextvars, merge_contextvars
from structlog.types import EventDict, WrappedLogger


def add_app_name(app_name: str) -> Callable[[WrappedLogger, str, EventDict], EventDict]:
    """Add application name to log."""
    distribution = pkg_resources.get_distribution(app_name)

    def processor(logger: WrappedLogger, name: str, event_dict: EventDict) -> EventDict:
        event_dict["app_name"] = distribution.project_name
        event_dict["version"] = distribution.version

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


def configure_logging(app_name: str, debug: bool = False) -> None:
    """Setup logging.

    Args:
        app_name: Application name.
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
                        add_app_name(app_name),
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
                app_name: {
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


@web.middleware
async def middleware(request, handler):
    """Logging middleware.

    Args:
        request: Current request instance.
        handler: Handler for request.
    """
    clear_contextvars()

    context_vars = {
        "request_id": request.headers.get("X-B3-Traceid", str(uuid4().hex)),
        "request_method": request.method,
    }

    if "X-Correlation-ID" in request.headers:
        context_vars["correlation_id"] = request.headers["X-Correlation-ID"]

    bind_contextvars(**context_vars)

    resp = await handler(request)

    bind_contextvars(response_status=resp.status)
    return resp


def setup(app: web.Application) -> None:
    """Setup application logger.

    Args:
        app: Application instance.
        debug: Application

    """
    configure_logging(app_name=app["app_name"], debug=app["debug"])

    app.logger = structlog.get_logger(app["app_name"])
    app.middlewares.append(middleware)  # type: ignore
