import os

import config
from aiohttp import web
from aiohttp_metrics import setup as setup_metrics  # type: ignore
from aiohttp_micro import (  # type: ignore
    AppConfig as BaseConfig,
    setup as setup_micro,
)
from aiohttp_openapi import setup as setup_openapi  # type: ignore
from aiohttp_storage import (  # type: ignore
    setup as setup_storage,
    StorageConfig,
)
from passport.client import PassportConfig, setup as setup_passport

from wallet.web import accounts


class AppConfig(BaseConfig):
    db = config.NestedField[StorageConfig](StorageConfig)
    passport = config.NestedField[PassportConfig](PassportConfig)


def init(app_name: str, config: AppConfig) -> web.Application:
    app = web.Application()

    app["app_root"] = os.path.dirname(__file__)

    setup_micro(app, app_name=app_name, config=config)
    setup_metrics(app, app_name=app_name)
    setup_storage(
        app,
        root=os.path.join(app["app_root"], "storage"),
        config=app["config"].db,
    )

    setup_passport(app)

    # Account endpoints
    app.router.add_get(
        "/api/accounts", accounts.search, name="api.accounts.show"
    )
    app.router.add_post("/api/accounts", accounts.add, name="api.accounts.add")
    app.router.add_put(
        r"/api/accounts/{account_key:\d+}",
        accounts.update,
        name="api.accounts.update",
    )
    app.router.add_delete(
        r"/api/accounts/{account_key:\d+}",
        accounts.remove,
        name="api.accounts.remove",
    )
    app.router.add_get(
        r"/api/accounts/{account_key:\d+}/balance",
        accounts.balance,
        name="api.accounts.balance",
    )

    setup_openapi(
        app,
        title="Wallet",
        version=app["distribution"].version,
        description="Wallet service API",
    )

    return app
