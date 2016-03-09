import asyncio
import gc
import logging
import os
import socket
import ujson


from aiohttp import ClientSession
import pytest

from alembic.config import Config as AlembicConfig
from alembic import command


from wallet.app import init, create_config
from wallet.utils.handlers import reverse_url


config = create_config()


@pytest.yield_fixture
def loop(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    yield loop

    if not loop._closed:
        loop.stop()
        loop.run_forever()
        loop.close()
    gc.collect()
    asyncio.set_event_loop(None)


@pytest.yield_fixture('function')
def app(loop, request):
    logger = logging.getLogger('wallet')
    app = loop.run_until_complete(init(config, logger, loop=loop))

    directory = app['config'].get('MIGRATIONS_ROOT')
    db_uri = app['config'].get_sqlalchemy_dsn()

    conf = AlembicConfig(os.path.join(directory, 'alembic.ini'))
    conf.set_main_option('script_location', directory)
    conf.set_main_option('sqlalchemy.url', db_uri)

    command.upgrade(conf, revision='head')

    yield app

    command.downgrade(conf, revision='base')

    loop.run_until_complete(app.cleanup())


class Server(object):

    def __init__(self, app):
        self._app = app
        self._handler = None
        self._srv = None
        self._url = None

    def _find_unused_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]

    async def create(self):
        self._handler = self._app.make_handler(debug=False, keep_alive=False)

        port = self._find_unused_port()
        self._srv = await self._app.loop.create_server(
            self._handler, '127.0.0.1', port)
        self._url = 'http://127.0.0.1:{port}'.format(port=port)

    async def finish(self):
        await self._handler.finish_connections()
        await self._app.finish()
        self._srv.close()
        await self._srv.wait_closed()

    def reverse_url(self, route, parts=None):
        return ''.join((self._url, reverse_url(self._app, route, parts)))


@pytest.yield_fixture('function')
def server(app, request):
    server = Server(app)
    app.loop.run_until_complete(server.create())
    yield server
    app.loop.run_until_complete(server.finish())


class AsyncResponseContext:
    __slots__ = ('_request', '_response')

    def __init__(self, request):
        self._request = request
        self._response = None

    async def __aenter__(self):
        self._response = await self._request
        return self._response

    async def __aexit__(self, exc_type, exc, tb):
        try:
            self._response.close()
        finally:
            self._response = None
            self._request = None


class HTTPClient:
    def __init__(self, session, app, url):
        self._app = app
        self._session = session
        self._url = url

    def reverse_url(self, route, parts=None):
        return ''.join((self._url, reverse_url(self._app, route, parts)))

    def request(self, method, endpoint, endpoint_params=None, **kwargs):
        if kwargs:
            if kwargs.pop('json', None):
                headers = kwargs.pop('headers', {})
                headers['content-type'] = 'application/json'

                kwargs['headers'] = headers
                kwargs['data'] = ujson.dumps(kwargs.pop('data', ''))

        kwargs.setdefault('url', self.reverse_url(endpoint, endpoint_params))
        return AsyncResponseContext(self._session.request(method, **kwargs))

    async def get_auth_token(self, credentials, endpoint='auth.login'):
        params = {
            'json': True,
            'data': credentials,
            'endpoint': endpoint
        }

        async with self.request('POST', **params) as response:
            assert response.status == 200
            token = response.headers.get('X-ACCESS-TOKEN', None)
            assert token
        return token

    def close(self):
        self._session.close()


@pytest.yield_fixture('function')
def client(server, request):
    client = HTTPClient(ClientSession(loop=server._app.loop), server._app,
                        server._url)
    yield client
    client.close()


@pytest.mark.tryfirst
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name):
        if not callable(obj):
            return
        item = pytest.Function(name, parent=collector)
        if 'run_loop' in item.keywords:
            return list(collector._genfunctions(name, obj))


@pytest.mark.tryfirst
def pytest_pyfunc_call(pyfuncitem):
    if 'run_loop' in pyfuncitem.keywords:
        funcargs = pyfuncitem.funcargs
        loop = funcargs['loop']
        testargs = {arg: funcargs[arg]
                    for arg in pyfuncitem._fixtureinfo.argnames}
        loop.run_until_complete(pyfuncitem.obj(**testargs))
        return True


def pytest_runtest_setup(item):
    if 'run_loop' in item.keywords and 'loop' not in item.fixturenames:
        item.fixturenames.append('loop')
