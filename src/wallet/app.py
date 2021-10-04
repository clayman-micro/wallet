import os
from typing import AsyncGenerator

import config
from aiohttp import ClientSession, web
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
from passport.client import PassportConfig

from wallet.openapi import setup as setup_openapi
from wallet.web.handlers import accounts, categories, operations
from wallet.web.middlewares.common import middleware as common_middleware
from wallet.web.middlewares.passport import middleware as passport_middleware


class AppConfig(BaseConfig):
    """Application config."""

    db = config.NestedField[StorageConfig](StorageConfig)
    passport = config.NestedField[PassportConfig](PassportConfig)


async def passport_ctx(app: web.Application) -> AsyncGenerator[None, None]:
    """Prepare application for Passport."""
    config = app["config"]

    app["logger"].debug("Fetch passport keys")

    if not config.passport.host:
        app["logger"].error("Passport host should be defined")
        raise RuntimeError("Passport host should be defined")

    if not config.passport.public_key:
        verify_ssl = True
        if app["config"].debug:
            verify_ssl = False

        url = f"{config.passport.host}/api/keys"

        async with ClientSession() as session:
            async with session.get(url, ssl=verify_ssl) as resp:
                if resp.status != 200:
                    app["logger"].error("Fetch passport keys failed", status=resp.status)
                    raise RuntimeError("Could not fetch passport keys")

                keys = await resp.json()

                config.passport.public_key = keys["public"]

    yield


def setup_passport(app: web.Application) -> None:
    """Setup passport integration.

    Args:
        app: Application instance.
    """
    app.cleanup_ctx.append(passport_ctx)
    app.middlewares.append(passport_middleware)


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
