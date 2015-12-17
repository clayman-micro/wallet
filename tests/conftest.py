import asyncio
from functools import wraps
import os
import socket
import ujson
from aiohttp import request
import pytest

from alembic.config import Config as AlembicConfig
from alembic import command


from wallet.app import create_app, create_config, destroy_app
from wallet.utils import reverse_url

config = create_config()


@pytest.yield_fixture('function')
def application(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    app = loop.run_until_complete(create_app(config, loop=loop))

    yield app

    loop.run_until_complete(destroy_app(app))
    loop.run_until_complete(app.finish())
    loop.close()


class ResponseContextManager(object):
    __slots__ = ('_response', )

    def __init__(self, response):
        self._response = response

    def __enter__(self):
        return self._response

    def __exit__(self, *args):
        try:
            self._response.close()
        finally:
            self._response = None


class Server(object):

    def __init__(self, app):
        self._app = app
        self._domain = None

    @property
    def domain(self):
        return self._domain

    @staticmethod
    def _find_unused_port():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        return port

    @asyncio.coroutine
    def create(self):
        port = Server._find_unused_port()
        srv = yield from self._app.loop.create_server(
            self._app.make_handler(keep_alive=False), '127.0.0.1', port)
        self._domain = 'http://127.0.0.1:{port}'.format(port=port)
        return srv

    @asyncio.coroutine
    def request(self, method, **kwargs):
        if kwargs:
            if kwargs.pop('json', None):
                headers = kwargs.pop('headers', {})
                headers['content-type'] = 'application/json'
                kwargs['headers'] = headers
                kwargs['data'] = ujson.dumps(kwargs.pop('data', ''))
        kwargs.setdefault('loop', self._app.loop)
        return (yield from request(method, **kwargs))

    def reverse_url(self, route, parts=None):
        return ''.join((self._domain, reverse_url(self._app, route, parts)))

    @asyncio.coroutine
    def get_auth_token(self, credentials):
        params = {
            'json': True,
            'data': credentials,
            'url': ''.join((self._domain,
                            self._app.router['auth.login'].url()))
        }
        with (yield from self.response_ctx('POST', **params)) as response:
            assert response.status == 200
            token = response.headers.get('X-ACCESS-TOKEN', None)
            assert token
        return token

    @asyncio.coroutine
    def response_ctx(self, method, **kwargs):
        response = yield from self.request(method, **kwargs)
        return ResponseContextManager(response)


@pytest.yield_fixture('function')
def server(application, request):
    server = Server(application)
    srv = application.loop.run_until_complete(server.create())

    yield server

    srv.close()


def async_test(create_database=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            application = kwargs.get('application')
            func = asyncio.coroutine(f)

            config = None
            if create_database:
                directory = application['config'].get('MIGRATIONS_ROOT')
                db_uri = application['config'].get_sqlalchemy_dsn()

                config = AlembicConfig(os.path.join(directory, 'alembic.ini'))
                config.set_main_option('script_location', directory)
                config.set_main_option('sqlalchemy.url', db_uri)

                command.upgrade(config, revision='head')

            try:
                application.loop.run_until_complete(func(*args, **kwargs))
            finally:
                engine = application['engine']
                engine.close()

                application.loop.run_until_complete(engine.wait_closed())

                if create_database:
                    command.downgrade(config, revision='base')

        return wrapper
    return decorator
