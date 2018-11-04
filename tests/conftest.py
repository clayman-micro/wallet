import logging

import faker
import pytest

from wallet.app import configure, init


@pytest.fixture(scope='session')
def fake():
    return faker.Faker()


@pytest.fixture(scope='session')
def config():
    conf = configure(defaults={
        'secret_key': 'secret',

        'passport_dsn': 'foo',

        'app_name': 'wallet',
        'app_host': 'localhost',
        'app_port': '5000'
    })

    return conf


@pytest.yield_fixture(scope='function')
def app(loop, pg_server, config):
    logger = logging.getLogger('app')

    config.update(db_name=pg_server['params']['database'],
                  db_user=pg_server['params']['user'],
                  db_password=pg_server['params']['password'],
                  db_host=pg_server['params']['host'],
                  db_port=pg_server['params']['port'])

    app = loop.run_until_complete(init(config, logger))


    yield app


    loop.run_until_complete(app.cleanup())
