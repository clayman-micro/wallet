import asyncio
from contextlib import contextmanager
import os

from aiohttp import web
from aiopg.sa import create_engine
import itsdangerous

from .handlers import base, core, accounts, auth, categories, transactions


@contextmanager
def add_route_ctx(app, handlers, url_prefix=None, name_prefix=None):
    def add_route(method, path, handler_name):
        handler = getattr(handlers, handler_name, None)

        if handler:
            url = path
            if url_prefix:
                url = '/'.join((url_prefix.rstrip('/'), url.lstrip('/')))

            if name_prefix:
                handler_name = '.'.join((name_prefix, handler_name))

            return app.router.add_route(method, url, handler, name=handler_name)
        else:
            return None
    yield add_route


@contextmanager
def register_handler_ctx(app, url_prefix=None, name_prefix=None):
    def register_handler(handler):
        if not isinstance(handler, base.BaseHandler):
            raise Exception('Handler improperly configured.')

        for method, url, endpoint_name in handler.endpoints:
            endpoint = getattr(handler, method.lower(), None)
            if not endpoint:
                continue

            if url_prefix:
                url = '/'.join((url_prefix.rstrip('/'), url.lstrip('/')))

            if name_prefix:
                endpoint_name = '.'.join((name_prefix, endpoint_name))

            app.router.add_route(method, url, endpoint, name=endpoint_name)
    yield register_handler


class Application(web.Application):

    def __init__(self, **kwargs):
        self.engine = None

        self.config = {
            'PROJECT_NAME': 'wallet',

            'DB_HOST': os.environ.get('DB_PORT_5432_TCP_ADDR', 'localhost'),
            'DB_PORT': os.environ.get('DB_PORT_5432_TCP_PORT', 5432),
            'DB_NAME': os.environ.get('DB_NAME', 'wallet'),
            'DB_USER': os.environ.get('DB_USER', 'wallet'),
            'DB_PASSWORD': os.environ.get('DB_PASSWORD', 'wallet'),

            'APP_ROOT': os.path.realpath(os.path.dirname(
                os.path.abspath(__file__))),

            'SECRET_KEY': 'top-secret',
            'TOKEN_EXPIRES': 300
        }

        # Configure folders
        self.config['MIGRATIONS_ROOT'] = os.path.join(
            self.config['APP_ROOT'], 'models', 'migrations')

        self.config['TEMPLATES_ROOT'] = os.path.join(self.config['APP_ROOT'],
                                                     'templates')

        # Make database dsn
        uri = 'postgres://{0}:{1}@{2}:{3}/{4}'.format(
            self.config.get('DB_USER'), self.config.get('DB_PASSWORD'),
            self.config.get('DB_HOST'), self.config.get('DB_PORT'),
            self.config.get('DB_NAME'))
        self.config['SQLALCHEMY_DSN'] = uri

        super(Application, self).__init__(**kwargs)

        self.signer = itsdangerous.TimedJSONWebSignatureSerializer(
            self.config.get('SECRET_KEY'),
            expires_in=self.config.get('TOKEN_EXPIRES')
        )

    @asyncio.coroutine
    def configure(self):
        self.engine = yield from create_engine(
            self.config.get('SQLALCHEMY_DSN'), loop=self.loop)

        with register_handler_ctx(self, name_prefix='core') as register_handler:
            register_handler(core.IndexHandler())

        with register_handler_ctx(self, '/auth', 'auth') as register_handler:
            register_handler(auth.RegistrationHandler())
            register_handler(auth.LoginHandler())

        with register_handler_ctx(self, '/api', 'api') as register_handler:
            register_handler(accounts.AccountAPIHandler())
            register_handler(categories.CategoryAPIHandler())
            register_handler(transactions.TransactionAPIHandler())
            register_handler(transactions.TransactionDetailAPIHandler())

    @asyncio.coroutine
    def close(self):
        if self.engine:
            self.engine.close()
