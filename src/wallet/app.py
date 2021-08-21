import os

import config
from aiohttp import web
from aiohttp.hdrs import METH_GET, METH_POST
from aiohttp_micro import (  # type: ignore
    AppConfig as BaseConfig,
    setup as setup_micro,
    setup_logging,
    setup_metrics,
)
from aiohttp_storage import (  # type: ignore
    setup as setup_storage,
    StorageConfig,
)
from passport.client import passport_ctx, PassportConfig

from wallet.openapi import setup as setup_openapi
from wallet.web.handlers import accounts, categories, operations
from wallet.web.middlewares.common import middleware as common_middleware
from wallet.web.middlewares.passport import middleware as passport_middleware


class AppConfig(BaseConfig):
    db = config.NestedField[StorageConfig](StorageConfig)
    passport = config.NestedField[PassportConfig](PassportConfig)


def setup_passport(app: web.Application) -> None:
    app.cleanup_ctx.append(passport_ctx)
    app.middlewares.append(passport_middleware)


def init(app_name: str, config: AppConfig) -> web.Application:
    app = web.Application()

    app["app_root"] = os.path.dirname(__file__)

    setup_micro(app, app_name=app_name, config=config)
    setup_storage(
        app, root=os.path.join(app["app_root"], "storage"), config=app["config"].db,
    )

    setup_metrics(app)
    setup_logging(app)

    app.middlewares.append(common_middleware)

    setup_passport(app)

    setup_openapi(
        app,
        title="Wallet",
        version=app["distribution"].version,
        description="Personal finance planning service",
        operations=[
            # Account operations
            (
                METH_GET,
                "/api/accounts",
                accounts.GetAccountsView(name="getAccounts", security="TokenAuth", tags=["accounts"]),
            ),
            (
                METH_POST,
                "/api/accounts",
                accounts.AddAccountView(name="getAccount", security="TokenAuth", tags=["accounts"]),
            ),
            # Category operations
            (
                METH_GET,
                "/api/categories",
                categories.GetCategoriesView(name="getCategories", security="TokenAuth", tags=["categories"]),
            ),
            (
                METH_POST,
                "/api/categories",
                categories.AddCategoryView(name="addCategory", security="TokenAuth", tags=["categories"]),
            ),
            # Operation operations
            (
                METH_GET,
                "/api/operations",
                operations.GetOperationsView(name="getOperations", security="TokenAuth", tags=["operations"]),
            ),
            (
                METH_POST,
                "/api/operations",
                operations.AddOperationView(name="addOperation", security="TokenAuth", tags=["operations"]),
            ),
        ],
        security=("TokenAuth", {"type": "apiKey", "name": "X-Access-Token", "in": "header"}),
    )

    return app
