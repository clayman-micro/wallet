import ujson
from aiohttp import web, ClientSession
from aiopg.sa import create_engine
from raven import Client, os
from raven_aiohttp import AioHttpTransport

from .config import Config
from .handlers import (auth, index, accounts, balance, categories,
                       transactions, details)

from .utils.handlers import register_handler


async def init(config: Config, logger, loop) -> web.Application:
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

    auth.register(app)
    accounts.register(app, '/api/accounts', 'api')
    balance.register(app, '/api/accounts/{account_id}', 'api')
    categories.register(app, '/api/categories', 'api')
    transactions.register(app, '/api/transactions', 'api')
    details.register(app, '/api/transactions/{transaction_id}/details', 'api')

    return app


async def register_service(app):
    config = app['config']

    app['config']['CONSUL_SERVICE'] = 'wallet_%s' % config.get('APP_HOSTNAME')
    payload = {
        'ID': app['config']['CONSUL_SERVICE'],
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
    app.logger.info('Register service "%s"' % app['config']['CONSUL_SERVICE'])


async def unregister_service(app):
    config = app['config']

    if 'CONSUL_SERVICE' in app['config']:
        service_id = app['config']['CONSUL_SERVICE']
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
