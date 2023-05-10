import socket
from importlib.metadata import Distribution

import punq
from aiohttp import web
from structlog.types import WrappedLogger

from wallet.web.handlers import meta
from wallet.web.middlewares.logging import logging_middleware
from wallet.web.middlewares.metrics import metrics_middleware


def create_container(logger: WrappedLogger) -> punq.Container:
    """Create IoC container for application."""
    container = punq.Container()

    container.register(WrappedLogger, instance=logger)

    return container


def init(
    dist: Distribution, container: punq.Container, debug: bool = False
) -> web.Application:
    """Create application instance.

    Args:
        dist: Application distribution.
        container: IoC contianer.
        debug: Run application in debug mode.

    Return:
        New application instance.
    """
    app = web.Application(
        middlewares=(logging_middleware, metrics_middleware),
        logger=container.resolve(WrappedLogger),
    )

    app["hostname"] = socket.gethostname()
    app["distribution"] = dist

    app["debug"] = debug
    app["container"] = container

    app.router.add_routes(routes=meta.routes)

    return app
