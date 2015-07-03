import asyncio
from contextlib import contextmanager
from functools import wraps, partial
import os
import socket
import ujson
import time
from aiohttp import request
import pytest

from alembic.config import Config as AlembicConfig
from alembic import command


from wallet import Application


@pytest.yield_fixture('function')
def application(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    app = Application(loop=loop)
    loop.run_until_complete(app.configure())

    yield app

    loop.run_until_complete(app.close())
    loop.run_until_complete(app.finish())
    loop.close()


@pytest.fixture('function')
def db(application, request):
    directory = application.config.get('MIGRATIONS_ROOT')
    db_uri = application.config.get('SQLALCHEMY_DSN')

    config = AlembicConfig(os.path.join(directory, 'alembic.ini'))
    config.set_main_option('script_location', directory)
    config.set_main_option('sqlalchemy.url', db_uri)

    command.upgrade(config, revision='head')

    def teardown():
        command.downgrade(config, revision='base')

    request.addfinalizer(teardown)
    return None


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

    def reverse_url(self, endpoint=None, parts=None):
        assert self._domain

        if not endpoint:
            return self._domain

        url = [self._domain, ]
        if parts:
            url.append(self._app.router[endpoint].url(parts=parts))
        else:
            url.append(self._app.router[endpoint].url())
        return ''.join(url)

    @asyncio.coroutine
    def request(self, method, endpoint=None, endpoint_params=None, **extra):
        params = {
            'url': self.reverse_url(endpoint, endpoint_params),
            'loop': self._app.loop
        }
        if extra:
            if extra.pop('json', None):
                headers = extra.pop('headers', {})
                headers['content-type'] = 'application/json'
                params['headers'] = headers
                params['data'] = ujson.dumps(extra.pop('data'), '')
            params.update(**extra)
        return (yield from request(method, **params))

    @asyncio.coroutine
    def response_ctx(self, method, endpoint=None, endpoint_params=None, **extra):
        response = (yield from self.request(method, endpoint,
                                                 endpoint_params, **extra))
        return ResponseContextManager(response)


def async_test(attach_server=False):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            application = kwargs.get('application')
            func = asyncio.coroutine(f)

            if attach_server:
                server = Server(application)
                srv = application.loop.run_until_complete(server.create())
                kwargs['server'] = server

            application.loop.run_until_complete(func(*args, **kwargs))

        return wrapper
    return decorator
