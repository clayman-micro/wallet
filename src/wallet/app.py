import socket

import pkg_resources
from aiohttp import web

from wallet.logging import setup as setup_logging
from wallet.metrics import setup as setup_metrics
from wallet.web import meta


def init(app_name: str, debug: bool = False) -> web.Application:
    """Create application instance.

    Args:
        app_name: Application name.
        debug: Run application in debug mode.

    Return:
        New application instance.
    """
    app = web.Application()

    app["app_name"] = app_name
    app["hostname"] = socket.gethostname()
    app["distribution"] = pkg_resources.get_distribution(app_name)

    app["debug"] = debug

    setup_logging(app)
    setup_metrics(app)

    app.router.add_get("/-/meta", handler=meta.index, name="meta", allow_head=False)
    app.router.add_get("/-/health", handler=meta.health, name="health", allow_head=False)

    return app
