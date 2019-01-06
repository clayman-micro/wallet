import logging
import os
from typing import AsyncGenerator, Dict, Optional

import pkg_resources
from aiohttp import web
from asyncpg.pool import create_pool  # type: ignore
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram  # type: ignore
from raven import Client as Raven  # type: ignore
from raven_aiohttp import AioHttpTransport  # type: ignore

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
        middlewares=[
            core.catch_exceptions_middleware,
            core.prometheus_middleware,
            users.auth_middleware,
        ],
    )

    app["config"] = config

    app["passport"] = users.PassportProvider(config["passport_dsn"])

    if config.get("sentry_dsn", None):
        app["raven"] = Raven(config["sentry_dsn"], transport=AioHttpTransport)

    app["distribution"] = pkg_resources.get_distribution("wallet")

    app["metrics_registry"] = CollectorRegistry()
    app["metrics"] = {
        "REQUEST_COUNT": Counter(
            "requests_total",
            "Total request count",
            ["app_name", "method", "endpoint", "http_status"],
            registry=app["metrics_registry"],
        ),
        "REQUEST_LATENCY": Histogram(
            "requests_latency_seconds",
            "Request latency",
            ["app_name", "endpoint"],
            registry=app["metrics_registry"],
        ),
        "REQUEST_IN_PROGRESS": Gauge(
            "requests_in_progress_total",
            "Requests in progress",
            ["app_name", "endpoint", "method"],
            registry=app["metrics_registry"],
        ),
    }

    app.cleanup_ctx.append(db_engine)

    app.router.add_routes(
        [
            web.get("/", core.index, name="index"),
            web.get("/-/health", core.health, name="health"),
            web.get("/-/metrics", core.metrics, name="metrics"),
        ]
    )

    app.router.add_routes(
        [
            web.get("/api/accounts", accounts.search, name="api.accounts"),
            web.post("/api/accounts", accounts.register, name="api.accounts.register"),
            web.put(
                r"/api/accounts/{account_key:\d+}", accounts.update, name="api.accounts.update"
            ),
            web.delete(
                r"/api/accounts/{account_key:\d+}", accounts.remove, name="api.accounts.remove"
            ),
        ]
    )

    app.router.add_routes(
        [
            web.get(
                r"/api/accounts/{account_key:\d+}/operations",
                operations.search,
                name="api.operations.search",
            ),
            web.post(
                r"/api/accounts/{account_key:\d+}/operations",
                operations.add,
                name="api.operations.add",
            ),
            web.get(
                r"/api/accounts/{account_key:\d+}/operations/{operation_key:\d+}",
                operations.fetch,
                name="api.operations.fetch",
            ),
            web.delete(
                r"/api/accounts/{account_key:\d+}/operations/{operation_key:\d+}",
                operations.remove,
                name="api.operations.remove",
            ),
        ]
    )

    app.router.add_routes(
        [
            web.get("/api/tags", tags.fetch, name="api.tags.fetch"),
            web.post("/api/tags", tags.add, name="api.tags.add"),
            web.delete(r"/api/tags/{tag_key:\d+}", tags.remove, name="api.tags.remove"),
        ]
    )

    return app


config_schema = {
    "app_name": {"type": "string", "required": True},
    "app_root": {"type": "string", "required": True},
    "app_hostname": {"type": "string"},
    "app_host": {"type": "string"},
    "app_port": {"type": "string"},
    "secret_key": {"type": "string", "required": True},
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


def configure(
    config_file: Optional[str] = None, defaults: Optional[Dict[str, str]] = None
) -> Config:
    config = Config(config_schema, defaults)  # type: ignore
    config["app_root"] = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))

    if config_file:
        config.update_from_yaml(config_file, True)

    for key in iter(config_schema.keys()):
        config.update_from_env_var(key)

    config.validate()

    return config
