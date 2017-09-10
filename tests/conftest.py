import logging
import subprocess
import time
from pathlib import Path

import docker as docker_client
import pytest
import requests

from wallet import configure, init


@pytest.fixture(scope='session')
def docker():
    return docker_client.from_env()


@pytest.fixture(scope='session')
def config():
    conf = configure(defaults={
        'secret_key': 'secret',

        'app_name': 'wallet',
        'app_host': 'localhost',
        'app_port': '5000'
    })

    return conf


@pytest.yield_fixture(scope='session')
def passport(docker, pg_server):
    image = 'clayman74/passport:2.2.1'

    name = pg_server['params']['database']
    user = pg_server['params']['user']
    password = pg_server['params']['password']
    host = pg_server['network']['IPAddress']

    conn = f'psql -h {host} -U {user}'
    env = {'PGPASSWORD': password}

    cmd = f'-d {name} -tAc "SELECT 1 FROM pg_database WHERE datname=\'passport\';"'  # noqa
    is_db_exists = docker.containers.run(image, ' '.join((conn, cmd)),
                                         environment=env)
    if not is_db_exists:
        cmd = f'-d {name} -c "CREATE DATABASE passport OWNER {user};"'
        try:
            docker.containers.run(image, ' '.join((conn, cmd)),
                                  environment={'PGPASSWORD': password},
                                  name='create_db')
        finally:
            container = docker.containers.get('create_db')
            container.remove()

    cmd = '-d passport -f /usr/local/usr/share/passport/upgrade_schema.sql'
    try:
        docker.containers.run(image, ' '.join((conn, cmd)),
                              environment={'PGPASSWORD': password},
                              name='apply_migrations')
    finally:
        container = docker.containers.get('apply_migrations')
        container.remove()

    container = docker.containers.create(
        image=image,
        command='passport server run --host=0.0.0.0 --port=5000',
        environment={
            'APP_NAME': 'passport',
            'DB_NAME': 'passport',
            'DB_HOST': host,
            'DB_USER': user,
            'DB_PASSWORD': password,
            'SECRET_KEY': 'top_secret'
        },
        ports={'5000/tcp': None},
        detach=True
    )

    container.start()
    container.reload()

    port = container.attrs['NetworkSettings']['Ports']['5000/tcp'][0]['HostPort']

    url = f'http://localhost:{port}'

    delay = 0.1
    for _ in range(100):
        try:
            r = requests.get(url)
            assert r.status_code == 200
            break
        except Exception:
            time.sleep(delay)
            delay *= 2
    else:
        pytest.fail('Cannot start passport service')

    yield url

    container.kill()
    container.remove()

    cmd = f'-d {name} -c "DROP DATABASE passport;"'
    try:
        docker.containers.run(image, ' '.join((conn, cmd)),
                              environment={'PGPASSWORD': password},
                              name='remove_db')
    finally:
        container = docker.containers.get('remove_db')
        container.remove()


@pytest.yield_fixture(scope='session')
def owner(passport):
    user = {'email': 'dev@clayman.pro', 'password': 'secret'}

    r = requests.post(f'{passport}/api/register', data=user)
    assert r.status_code == 201

    r = requests.post(f'{passport}/api/login', data=user)
    assert r.status_code == 200

    user['token'] = r.headers['X-ACCESS-TOKEN']

    r = requests.get(f'{passport}/api/identify',
                     headers={'X-ACCESS-TOKEN': user['token']})
    data = r.json()

    user['id'] = data['owner']['id']

    yield user


@pytest.yield_fixture(scope='function')
def client(loop, test_client, pg_server, config):
    logger = logging.getLogger('app')

    config.update(db_name=pg_server['params']['database'],
                  db_user=pg_server['params']['user'],
                  db_password=pg_server['params']['password'],
                  db_host=pg_server['params']['host'],
                  db_port=pg_server['params']['port'])

    app = loop.run_until_complete(init(config, logger, loop=loop))

    cwd = Path(config['app_root'])
    sql_root = cwd / 'storage' / 'sql'

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
