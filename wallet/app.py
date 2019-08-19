import logging
import os
from typing import AsyncGenerator, Dict, Optional

import pkg_resources
import sentry_sdk
from aiohttp import web
from aiohttp_metrics import setup as setup_metrics  # type: ignore
from asyncpg.pool import create_pool  # type: ignore
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from wallet.adapters.web import accounts, core, operations, tags, users
from wallet.config import Config


async def db_engine(app: web.Application) -> AsyncGenerator:
    config = app["config"]

    app["db"] = await create_pool(
        user=config["db_user"],
        database=config["db_name"],
        host=config["db_host"],
        password=config["db_password"],
        port=config["db_port"],
        min_size=1,
        max_size=10,
    )

    yield

    await app["db"].close()


async def init(config: Config, logger: logging.Logger) -> web.Application:
    app = web.Application(
        logger=logger,
        middlewares=[  # type: ignore
            core.catch_exceptions_middleware,
            users.auth_middleware,
        ],
    )

    app['app_name'] = 'wallet'

    app["config"] = config

    app["passport"] = users.PassportProvider(config["passport_dsn"])

    if config.get("sentry_dsn", None):
        sentry_sdk.init(dsn=config["sentry_dsn"], integrations=[AioHttpIntegration()])

    app["distribution"] = pkg_resources.get_distribution("wallet")

    setup_metrics(app)

    app.cleanup_ctx.append(db_engine)

    app.router.add_routes([
        web.get("/", core.index, name="index"),
        web.get("/-/health", core.health, name="health"),
    ])

    app.router.add_routes([
        web.get("/api/accounts", accounts.search, name="api.accounts"),
        web.post("/api/accounts", accounts.register, name="api.accounts.register"),
        web.get(r"/api/accounts/{account_key:\d+}/balance", accounts.balance,
                name="api.accounts.balance"),
        web.put(r"/api/accounts/{account_key:\d+}", accounts.update,
                name="api.accounts.update"),
        web.delete(r"/api/accounts/{account_key:\d+}", accounts.remove,
                   name="api.accounts.remove")
    ])

    app.router.add_routes([
        web.get(r"/api/accounts/{account_key:\d+}/operations", operations.search,
                name="api.operations.search"),
        web.post(r"/api/accounts/{account_key:\d+}/operations", operations.add,
                 name="api.operations.add"),
        web.get(r"/api/accounts/{account_key:\d+}/operations/{operation_key:\d+}",
                operations.fetch, name="api.operations.fetch"),
        web.delete(r"/api/accounts/{account_key:\d+}/operations/{operation_key:\d+}",
                   operations.remove, name="api.operations.remove"),

        web.post(r"/api/accounts/{account_key:\d+}/operations/{operation_key:\d+}/tags",
                 operations.add_tag, name="api.operations.add_tag"),
        web.delete(r"/api/accounts/{account_key:\d+}/operations/{operation_key:\d+}/tags/{tag_key:\d+}",
                   operations.remove_tag, name="api.operations.remove_tag")
    ])

    app.router.add_routes([
        web.get("/api/tags", tags.fetch, name="api.tags.fetch"),
        web.post("/api/tags", tags.add, name="api.tags.add"),
        web.delete(r"/api/tags/{tag_key:\d+}", tags.remove, name="api.tags.remove"),
    ])

    return app


config_schema = {
    "app_name": {"type": "string", "required": True},
    "app_root": {"type": "string", "required": True},
    "app_hostname": {"type": "string"},
    "app_host": {"type": "string"},
    "app_port": {"type": "string"},
    "access_log": {"type": "string", "required": True},
    "db_name": {"type": "string", "required": True},
    "db_user": {"type": "string", "required": True},
    "db_password": {"type": "string", "required": True},
    "db_host": {"type": "string", "required": True},
    "db_port": {"type": "integer", "required": True, "coerce": int},
    "consul_host": {"type": "string", "required": True},
    "consul_port": {"type": "integer", "required": True, "coerce": int},
    "sentry_dsn": {"type": "string"},
    "passport_dsn": {"type": "string"},
    "logging": {"type": "dict", "required": True},
}


def configure(defaults: Optional[Dict[str, str]] = None) -> Config:
    config = Config(config_schema, defaults)  # type: ignore
    config["app_root"] = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))

    for key in iter(config_schema.keys()):
        config.update_from_env_var(key)

    config.validate()

    return config
