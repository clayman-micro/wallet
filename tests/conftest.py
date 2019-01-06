import logging
import subprocess
from pathlib import Path
from typing import Any

import faker  # type: ignore
import pytest  # type: ignore
from aiohttp import web

from wallet.app import configure, init
from wallet.domain.entities import User


@pytest.fixture(scope="session")
def config():
    conf = configure(
        defaults={
            "secret_key": "secret",
            "passport_dsn": "foo",
            "app_name": "wallet",
            "app_host": "localhost",
            "app_port": "5000",
        }
    )

    return conf


@pytest.yield_fixture(scope="function")
def app(loop, pg_server, config):
    logger = logging.getLogger("app")

    config.update(
        db_name=pg_server["params"]["database"],
        db_user=pg_server["params"]["user"],
        db_password=pg_server["params"]["password"],
        db_host=pg_server["params"]["host"],
        db_port=pg_server["params"]["port"],
    )

    app = loop.run_until_complete(init(config, logger))
    runner = web.AppRunner(app)

    cwd = Path(config["app_root"])
    sql_root = cwd / "storage" / "sql"

    cmd = (
        "cat {schema} | PGPASSWORD='{password}' psql -h {host} -p {port} -d {database} -U {user}"
    )  # noqa

    subprocess.call(
        [
            cmd.format(
                schema=(sql_root / "upgrade_schema.sql").as_posix(),
                database=config["db_name"],
                host=config["db_host"],
                port=config["db_port"],
                user=config["db_user"],
                password=config["db_password"],
            )
        ],
        shell=True,
        cwd=cwd.as_posix(),
    )

    loop.run_until_complete(runner.setup())

    yield app

    loop.run_until_complete(runner.cleanup())

    subprocess.call(
        [
            cmd.format(
                schema=(sql_root / "downgrade_schema.sql").as_posix(),
                database=config["db_name"],
                host=config["db_host"],
                port=config["db_port"],
                user=config["db_user"],
                password=config["db_password"],
            )
        ],
        shell=True,
        cwd=cwd.as_posix(),
    )


@pytest.fixture(scope="session")
def fake():
    return faker.Faker()


@pytest.fixture(scope="function")
def user(fake: Any) -> User:
    return User(1, fake.free_email())
