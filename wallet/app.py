import asyncio

import ujson
from aiohttp import web, ClientSession
from aiopg.sa import create_engine, Engine
from raven import Client, os
from raven_aiohttp import AioHttpTransport

from .config import Config
from .handlers import auth, index
from .handlers.accounts import get_accounts, AccountResourceHandler
from .handlers.categories import get_categories, CategoryResourceHandler
from .handlers.transactions import get_transactions, TransactionResourceHandler
from .handlers.details import get_details, DetailResourceHandler

from .utils.handlers import register_handler


@asyncio.coroutine
def create_app(config: Config, loop) -> web.Application:
    app = web.Application(loop=loop)
    app['config'] = config

    # create database engine
    app['engine'] = yield from create_engine(
        config.get_sqlalchemy_dsn(), loop=loop)  # type: Engine

    # create sentry client
    sentry_dsn = config.get('SENTRY_DSN', None)
    if sentry_dsn:
        app['raven'] = Client(sentry_dsn, transport=AioHttpTransport)

    # Configure handlers
    with register_handler(app, name_prefix='core') as register:
        register('GET', '/', index, 'index')

    with register_handler(app, '/auth', 'auth') as register:
        register('POST', 'login', auth.login, 'login')
        register('POST', 'register', auth.register, 'registration')

    with register_handler(app, '/api', 'api') as register:
        register('GET', '/accounts', get_accounts, 'get_accounts')
        register('GET', '/categories', get_categories, 'get_categories')
        register('GET', '/transactions', get_transactions, 'get_transactions')
        register('GET', '/transactions/{transaction_id}/details', get_details,
                 'get_details')

    with register_handler(app, '/api/accounts', 'api') as register:
        handler = AccountResourceHandler()
        register('POST', '', handler, 'create_account')
        register('GET', '/{instance_id}', handler, 'get_account')
        register('PUT', '/{instance_id}', handler, 'update_account')
        register('DELETE', '/{instance_id}', handler, 'remove_account')

    with register_handler(app, '/api/categories', 'api') as register:
        handler = CategoryResourceHandler()
        register('POST', '', handler, 'create_category')
        register('GET', '/{instance_id}', handler, 'get_category')
        register('PUT', '/{instance_id}', handler, 'update_category')
        register('DELETE', '/{instance_id}', handler, 'remove_category')

    with register_handler(app, '/api/transactions', 'api') as register:
        handler = TransactionResourceHandler()
        register('POST', '', handler, 'create_transaction')
        register('GET', '/{instance_id}', handler, 'get_transaction')
        register('PUT', '/{instance_id}', handler, 'update_transaction')
        register('DELETE', '/{instance_id}', handler, 'remove_transaction')

    prefix = '/api/transactions/{transaction_id}/details'
    with register_handler(app, prefix, 'api') as register:
        handler = DetailResourceHandler()
        register('POST', '', handler, 'create_detail')
        register('GET', '/{instance_id}', handler, 'get_detail')
        register('PUT', '/{instance_id}', handler, 'update_detail')
        register('DELETE', '/{instance_id}', handler, 'remove_detail')

    return app


async def init(config: Config, logger, loop):
    app = web.Application(logger=logger, loop=loop)
    app['config'] = config

    # create database engine
    app['engine'] = await create_engine(config.get_sqlalchemy_dsn(), loop=loop)

    # create sentry client
    sentry_dsn = config.get('SENTRY_DSN', None)
    if sentry_dsn:
        app['raven'] = Client(sentry_dsn, transport=AioHttpTransport)

    async def close(app):
        app.logger.info('Closing app')
        await unregister_service(app)
        app['engine'].close()

    app.on_cleanup.append(close)

    # Configure handlers
    with register_handler(app, name_prefix='core') as register:
        register('GET', '/', index, 'index')

    return app


async def register_service(app):
    config = app['config']

    service_id = 'wallet_%s' % config.get('APP_HOSTNAME')
    payload = {
        'ID': service_id,
        'Name': 'wallet',
        'Tags': [
            'master', 'v1'
        ],
        'Address': config.get('APP_ADDRESS'),
        'Port': config.get('APP_PORT')
    }

    url = 'http://%s:%s/v1/agent/service/register' % (
        config.get('CONSUL_HOST'), config.get('CONSUL_PORT')
    )
    with ClientSession() as session:
        async with session.put(url, data=ujson.dumps(payload)) as resp:
            assert resp.status == 200
    app.logger.info('Register service "%s"' % service_id)


async def unregister_service(app):
    config = app['config']

    service_id = 'wallet_%s' % config.get('APP_HOSTNAME')
    url = 'http://%s:%s/v1/agent/service/deregister/%s' % (
        config.get('CONSUL_HOST'), config.get('CONSUL_PORT'), service_id
    )
    with ClientSession() as session:
        async with session.get(url) as resp:
            assert resp.status == 200
    app.logger.info('Remove service "%s" from Consul' % service_id)


def create_config(config=None) -> Config:
    app_root = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))

    conf = Config(None, {
        'project_name': 'wallet',

        'secret_key': 'top-secret',
        'token_expires': 300,

        'db_user': 'wallet',
        'db_password': '',
        'db_name': 'wallet',
        'db_host': 'localhost',
        'db_port': 5432,

        'app_root': app_root,
        'migrations_root': os.path.join(app_root, 'storage', 'migrations'),
    })

    if config:
        conf.from_yaml(config, silent=True)

    for param in ('secret_key', 'token_expires'):
        conf.from_envvar(param.upper(), silent=True)

    for param in ('host', 'port', 'user', 'password', 'name'):
        conf.from_envvar('DB_%s' % param.upper(), silent=True)

    for param in ('host', 'port'):
        conf.from_envvar('CONSUL_%s' % param.upper(), silent=True)

    for param in ('address', 'port'):
        conf.from_envvar('APP_%s' % param.upper(), silent=True)

    return conf
