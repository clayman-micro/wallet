import asyncio
from contextlib import contextmanager
import os

from aiohttp import web
from aiopg.sa import create_engine

from raven import Client
from raven_aiohttp import AioHttpTransport

from .handlers import base, core, accounts, auth, categories, transactions
from .config import Config


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

            for decorator in handler.decorators:
                endpoint = decorator(endpoint)

            app.router.add_route(method, url, endpoint, name=endpoint_name)
    yield register_handler


class Application(web.Application):

    def __init__(self, config=None, **kwargs):
        self.engine = None
        self.raven = None

        app_root = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))

        self.config = Config(None, {
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
            'templates_root': os.path.join(app_root, 'templates')
        })

        if config:
            self.config.from_json(config)

        for param in ('secret_key', 'token_expires'):
            self.config.from_envvar(param.upper(), silent=True)

        for param in ('host', 'port', 'user', 'password', 'name'):
            self.config.from_envvar('DB_%s' % param.upper(), silent=True)

        super(Application, self).__init__(**kwargs)

    def reverse_url(self, name, parts=None):
        return self.router[name].url(parts=parts) if parts \
            else self.router[name].url()

    @asyncio.coroutine
    def configure(self):
        self.engine = yield from create_engine(
            self.config.get_sqlalchemy_dsn(), loop=self.loop)

        sentry_dsn = self.config.get('SENTRY_DSN', None)
        if sentry_dsn:
            self.raven = Client(self.config.get('SENTRY_DSN'),
                                transport=AioHttpTransport, loop=self.loop)

        self.router.add_route('GET', '/', core.index, name='core.index')
        self.router.add_route('POST', '/auth/register', auth.register,
                              name='auth.registration')
        self.router.add_route('POST', '/auth/login', auth.login,
                              name='auth.login')

        with register_handler_ctx(self, '/api', 'api') as register_handler:
            register_handler(accounts.AccountAPIHandler())
            register_handler(categories.CategoryAPIHandler())
            register_handler(transactions.TransactionAPIHandler())
            register_handler(transactions.TransactionDetailAPIHandler())

    @asyncio.coroutine
    def close(self):
        if self.engine:
            self.engine.close()
