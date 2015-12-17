import asyncio

from aiohttp import web
from aiopg.sa import create_engine
from raven import Client, os
from raven_aiohttp import AioHttpTransport

from .config import Config
from .handlers import core, auth
from .utils import register_handler


@asyncio.coroutine
def create_app(config: Config, loop) -> web.Application:
    app = web.Application(loop=loop)
    app['config'] = config

    # create database engine
    app['engine'] = yield from create_engine(
        config.get_sqlalchemy_dsn(), loop=loop)

    # create sentry client
    sentry_dsn = config.get('SENTRY_DSN', None)
    if sentry_dsn:
        app['raven'] = Client(sentry_dsn, transport=AioHttpTransport)

    # Configure handlers
    with register_handler(app, url_prefix='/', name_prefix='core') as register:
        register('GET', '', core.index, 'index')

    with register_handler(app, '/auth', 'auth') as register:
        register('POST', 'login', auth.login, 'login')
        register('POST', 'register', auth.register, 'registration')

    return app


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
        conf.from_json(config, silent=True)

    for param in ('secret_key', 'token_expires'):
        conf.from_envvar(param.upper(), silent=True)

    for param in ('host', 'port', 'user', 'password', 'name'):
        conf.from_envvar('DB_%s' % param.upper(), silent=True)

    return conf


@asyncio.coroutine
def destroy_app(app: web.Application):
    if 'engine' in app and app['engine'] is not None:
        app['engine'].close()
