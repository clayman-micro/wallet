import os

from aiohttp import web
from aiohttp.hdrs import METH_GET, METH_POST
from aiohttp_micro import setup as setup_micro  # type: ignore
from aiohttp_micro import setup_logging, setup_metrics
from aiohttp_storage import setup as setup_storage  # type: ignore

from wallet.config import AppConfig
from wallet.openapi import setup as setup_openapi
from wallet.passport import setup as setup_passport
from wallet.web.handlers import accounts, categories, operations
from wallet.web.middlewares.common import middleware as common_middleware


def init(app_name: str, config: AppConfig) -> web.Application:
    """Create application instance.

    Args:
        app_name: New application name.
        config: Application config

    Returns:
        Application instance.
    """
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
