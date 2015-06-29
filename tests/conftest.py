import asyncio
from functools import wraps
import os
import socket
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


@asyncio.coroutine
def create_server(application):

    def find_unused_port():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        return port

    port = find_unused_port()
    srv = yield from application.loop.create_server(
        application.make_handler(keep_alive=False), '127.0.0.1', port)
    url = 'http://127.0.0.1:{port}'.format(port=port)
    return srv, url


def async_test(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        application = kwargs.get('application')
        func = asyncio.coroutine(f)
        application.loop.run_until_complete(func(*args, **kwargs))

    return wrapper