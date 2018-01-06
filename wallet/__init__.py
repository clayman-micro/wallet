import asyncio
import logging
import os
from typing import Dict

import pkg_resources
from aiohttp import web
from asyncpg.pool import create_pool, Pool
from raven import Client
from raven_aiohttp import AioHttpTransport

from wallet.config import Config
from wallet.gateways.owners import PassportGateway
from wallet.handlers import accounts, index, operations, register_handler
from wallet.middlewares import auth_middleware, catch_exceptions_middleware


class App(web.Application):
    def __init__(self, *args, config=None, **kwargs):
        super(App, self).__init__(**kwargs)

        self._config = config
        self._db = None
        self._distribution = pkg_resources.get_distribution('wallet')
        self._raven = None
        self._passport = None

    @property
    def config(self) -> Config:
        return self._config

    @property
    def db(self) -> Pool:
        return self._db

    @property
    def distribution(self):
        return self._distribution

    @property
    def passport(self) -> PassportGateway:
        return self._passport

    @property
    def raven(self) -> Client:
        return self._raven

    @db.setter  # noqa
    def db(self, value: Pool) -> None:
        self._db = value

    @passport.setter  # noqa
    def passport(self, value: PassportGateway) -> None:
        self._passport = value

    @raven.setter  # noqa
    def raven(self, value: Client) -> None:
        self._raven = value

    def copy(self):
        raise NotImplementedError


async def startup(app: App) -> None:
    app.logger.info('Application serving on {host}:{port}'.format(
        host=app.config['app_host'], port=app.config['app_port']))

    app.passport = PassportGateway(app.config.get('passport_dsn'))

    app.db = await create_pool(
        user=app.config.get('db_user'), database=app.config.get('db_name'),
        host=app.config.get('db_host'), password=app.config.get('db_password'),
        port=app.config.get('db_port'), min_size=1, max_size=10, loop=app.loop
    )

    if app.config.get('sentry_dsn', None):
        app.raven = Client(app.config['sentry_dsn'], transport=AioHttpTransport)


async def cleanup(instance: App) -> None:
    instance.logger.info('Good bye')

    if instance.db:
        await instance.db.close()


async def init(config: Config, logger: logging.Logger=None,
               loop: asyncio.AbstractEventLoop=None) -> App:

    app = App(config=config, logger=logger, loop=loop,
              middlewares=[catch_exceptions_middleware, auth_middleware])

    app.on_startup.append(startup)
    app.on_cleanup.append(cleanup)

    with register_handler(app, '/') as add:
        add('GET', '', index, 'index')

    with register_handler(app, '/api/accounts', 'api') as add:
        add('GET', '', accounts.get_accounts)
        add('POST', '', accounts.add_account)
        add('GET', '{instance_id}', accounts.get_account)
        add('PUT', '{instance_id}', accounts.update_account)
        add('DELETE', '{instance_id}', accounts.remove_account)

    url_prefix = '/api/accounts/{account}/operations'
    with register_handler(app, url_prefix, 'api') as add:
        add('GET', '', operations.get_operations)
        add('POST', '', operations.add_operation)
        add('GET', '{operation}', operations.get_operation)
        add('PUT', '{operation}', operations.update_operation)
        add('DELETE', '{operation}', operations.remove_operation)

    return app


config_schema = {
    'app_name': {'type': 'string', 'required': True},
    'app_root': {'type': 'string', 'required': True},
    'app_hostname': {'type': 'string'},
    'app_host': {'type': 'string'},
    'app_port': {'type': 'string'},

    'secret_key': {'type': 'string', 'required': True},

    'access_log': {'type': 'string', 'required': True},

    'db_name': {'type': 'string', 'required': True},
    'db_user': {'type': 'string', 'required': True},
    'db_password': {'type': 'string', 'required': True},
    'db_host': {'type': 'string', 'required': True},
    'db_port': {'type': 'integer', 'required': True, 'coerce': int},

    'consul_host': {'type': 'string', 'required': True},
    'consul_port': {'type': 'integer', 'required': True, 'coerce': int},

    'sentry_dsn': {'type': 'string'},

    'passport_dsn': {'type': 'string'},

    'logging': {'type': 'dict', 'required': True}
}


def configure(config_file: str=None, defaults: Dict=None) -> Config:
    config = Config(config_schema, defaults)
    config['app_root'] = os.path.realpath(os.path.dirname(
        os.path.abspath(__file__)))

    if config_file:
        config.update_from_yaml(config_file, True)

    for key in iter(config_schema.keys()):
        config.update_from_env_var(key)

    config.validate()

    return config
