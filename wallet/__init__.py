import asyncio
from contextlib import contextmanager
from datetime import datetime
import os

from aiohttp import web
from aiopg.sa import create_engine
import itsdangerous

from .handlers import core


@contextmanager
def add_route_ctx(app, handlers, url_prefix=None, name_prefix=None):
    def add_route(method, path, name):
        handler = getattr(handlers, name, None)

        if handler:
            url = path
            if url_prefix:
                url = '/'.join((url_prefix.rstrip('/'), url.lstrip('/')))

            if name_prefix:
                name = '.'.join((name_prefix, name))

            return app.router.add_route(method, url, handler, name=name)
        else:
            return None
    yield add_route


class Application(web.Application):

    def __init__(self, **kwargs):
        self.engine = None

        self.config = {
            'PROJECT_NAME': 'wallet',

            'DB_HOST': os.environ.get('DB_HOST', 'localhost'),
            'DB_PORT': os.environ.get('DB_PORT', 5432),
            'DB_NAME': os.environ.get('DB_NAME', 'wallet'),
            'DB_USER': os.environ.get('DB_USER', 'wallet'),
            'DB_PASSWORD': os.environ.get('DB_PASSWORD', ''),

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
            self.config.get('SQLALCHEMY_DSN'), loop=self.loop
        )

        with add_route_ctx(self, core, name_prefix='core') as add_route:
            add_route('GET', '/', 'index')

    @asyncio.coroutine
    def close(self):
        if self.engine:
            self.engine.close()