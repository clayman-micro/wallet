import logging
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from aiohttp.test_utils import make_mocked_coro

from wallet import configure, init
from wallet.entities import Owner


@pytest.fixture(scope='session')
def config():
    conf = configure(defaults={
        'secret_key': 'secret',

        'app_name': 'wallet',
        'app_host': 'localhost',
        'app_port': '5000'
    })

    return conf


@pytest.fixture(scope='function')
def owner():
    return Owner('test@clayman.pro', pk=1)


@pytest.fixture(scope='function')
def passport_gateway(owner):
    gateway_mock = MagicMock()
    gateway_mock.identify = make_mocked_coro(owner)

    return gateway_mock


@pytest.yield_fixture(scope='function')
def client(loop, test_client, passport_gateway, pg_server, config):
    logger = logging.getLogger('app')

    config.update(db_name=pg_server['params']['database'],
                  db_user=pg_server['params']['user'],
                  db_password=pg_server['params']['password'],
                  db_host=pg_server['params']['host'],
                  db_port=pg_server['params']['port'])

    app = loop.run_until_complete(init(config, logger, loop=loop))

    cwd = Path(config['app_root'])
    sql_root = cwd / 'repositories' / 'sql'

    cmd = 'cat {schema} | PGPASSWORD=\'{password}\' psql -h {host} -p {port} -d {database} -U {user}'  # noqa

    subprocess.call([cmd.format(
        schema=(sql_root / 'upgrade_schema.sql').as_posix(),
        database=config['db_name'],
        host=config['db_host'], port=config['db_port'],
        user=config['db_user'], password=config['db_password'],
    )], shell=True, cwd=cwd.as_posix())

    yield loop.run_until_complete(test_client(app))

    subprocess.call([cmd.format(
        schema=(sql_root / 'downgrade_schema.sql').as_posix(),
        database=config['db_name'],
        host=config['db_host'], port=config['db_port'],
        user=config['db_user'], password=config['db_password'],
    )], shell=True, cwd=cwd.as_posix())

    loop.run_until_complete(app.cleanup())
