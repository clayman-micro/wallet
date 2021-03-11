from pathlib import Path
from typing import Any

import faker  # type: ignore
import pendulum  # type: ignore
import pytest  # type: ignore
import ujson  # type: ignore
from aiohttp import web
from aiohttp_storage.tests import storage  # type: ignore
from passport.domain import User  # type: ignore

from wallet.app import AppConfig, init


@pytest.fixture(scope="session")
def fake():
    return faker.Faker()


@pytest.fixture(scope="function")
def user(fake: Any) -> User:
    return User(key=1, email=fake.free_email())


@pytest.fixture(scope="session")
def config():
    conf = AppConfig()

    return conf


@pytest.yield_fixture(scope="function")
def app(pg_server, config):
    config.db.host = pg_server["params"]["host"]
    config.db.port = pg_server["params"]["port"]
    config.db.user = pg_server["params"]["user"]
    config.db.password = pg_server["params"]["password"]
    config.db.database = pg_server["params"]["database"]

    app = init("wallet", config)

    with storage(config=app["config"].db, root=app["storage_root"]):
        yield app


@pytest.yield_fixture(scope="function")
async def prepared_app(app):
    runner = web.AppRunner(app)
    await runner.setup()

    yield app

    await runner.cleanup()


@pytest.fixture(scope="function")
async def client(app, aiohttp_client):
    client = await aiohttp_client(app)

    return client


@pytest.fixture(scope="session")
def today():
    return pendulum.today()


@pytest.fixture(scope="session")
def month(today):
    return today.start_of("month").date()


def load_test_cases(cwd, test_cases):
    with open(Path(cwd).parent / "test_cases" / test_cases, "r") as fp:
        for test_case in ujson.loads(fp.read()):
            yield test_case
