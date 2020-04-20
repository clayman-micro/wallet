import config
from aiohttp import web
from aiohttp_metrics import setup as setup_metrics  # type: ignore
from aiohttp_micro import (  # type: ignore
    AppConfig as BaseConfig,
    setup as setup_micro,
)
from asyncpg.pool import create_pool  # type: ignore
from passport.app import TokenConfig  # type: ignore

from wallet.handlers import accounts, operations


class AppConfig(BaseConfig):
    db = config.NestedField(config.PostgresConfig)
    tokens = config.NestedField(TokenConfig)


async def db_engine(app: web.Application) -> None:
    config: AppConfig = app["config"]

    app["db"] = await create_pool(
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
        database=config.db.database,
        min_size=config.db.min_pool_size,
        max_size=config.db.max_pool_size,
    )

    yield

    await app["db"].close()


async def init(app_name: str, config: AppConfig) -> web.Application:
    app = web.Application()

    setup_micro(app, app_name=app_name, config=config)
    setup_metrics(app, app_name=app_name)

    app.cleanup_ctx.append(db_engine)

    app.router.add_routes(
        [
            web.get("/api/accounts", accounts.search, name="api.accounts"),
            web.post(
                "/api/accounts", accounts.register, name="api.accounts.register"
            ),
            web.get(
                r"/api/accounts/{account_key:\d+}/balance",
                accounts.balance,
                name="api.accounts.balance",
            ),
            web.put(
                r"/api/accounts/{account_key:\d+}",
                accounts.update,
                name="api.accounts.update",
            ),
            web.delete(
                r"/api/accounts/{account_key:\d+}",
                accounts.remove,
                name="api.accounts.remove",
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
                r"/api/accounts/{account_key:\d+}/operations/{operation_key:\d+}",  # noqa: E501
                operations.fetch,
                name="api.operations.fetch",
            ),
            web.delete(
                r"/api/accounts/{account_key:\d+}/operations/{operation_key:\d+}",  # noqa: E501
                operations.remove,
                name="api.operations.remove",
            ),
        ]
    )

    return app
