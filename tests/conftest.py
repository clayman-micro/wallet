import os
import subprocess
from pathlib import Path
from typing import Any

import faker  # type: ignore
import pendulum  # type: ignore
import pytest  # type: ignore
from aiohttp import web
from passport.domain import User  # type: ignore

from wallet.app import AppConfig, init


@pytest.fixture(scope="session")
def config():
    conf = AppConfig()

    conf.tokens.public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQDBqkP6h/7LMOAaWuVAqjPcrOdUCiMhyykbMaDji8odBKtCam1MyBxq1I87LFiAbHx7r5biBMUC/nyTzPiYF5II+g4MDLgV5S8/6uTmtCL40FsuIOClFPqbAiitvRFYDuBTJx3w1Fr4zWWIVtaUFqer5nAsnr4sovOG+zRVtfXJ8w=="  # noqa
    conf.tokens.private_key = """
-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQDBqkP6h/7LMOAaWuVAqjPcrOdUCiMhyykbMaDji8odBKtCam1M
yBxq1I87LFiAbHx7r5biBMUC/nyTzPiYF5II+g4MDLgV5S8/6uTmtCL40FsuIOCl
FPqbAiitvRFYDuBTJx3w1Fr4zWWIVtaUFqer5nAsnr4sovOG+zRVtfXJ8wIDAQAB
AoGBAKiSIQuwVmrdByRJnCU2QWBDLDQtgrkGkqg2AZou8mVhzARKiQr9YCbpECds
iTh3tb8fbtEbX7UkeKFaF8SjN5uPCIX6MVoQDoH8VTmsj6lFIXpeCjfqEXEFdE/p
AAJVGZBxN0VNmpVYpp1XhGQE4iI7WBUZtJ7stP0WcjkXkzsRAkEA4h9aGY7bbHru
lX7PgguP+FMMcOSc+Ax7oQuBZ0x0zXO1YVE1vl4KHeDSuATI6bT4LYGJFa3soUnF
PMFi6MacGwJBANtBCP1h7LdOFWRtVpOCNCjNYGeuRzxJ3APiolnMpTsUQ8qDWa+M
UrcO0WhUy7Z+swicEDuKO0CoOjkOQFhZtwkCQQCTFFmCrk1DLmLpkmZe7C5lE3/Q
HqOLJHN1uQoeqrh+uniMKEqQ3JIwBQCK+XHFshSLZOpJ06tK7bUBY7h2OFlpAkBK
EOcziXAI4ETTvyfe/r4WBoMJo1MHJ8A+Q8IqabprgcYA1GxopBORKV1OTE7g4F4k
i2vkYSbxCaNZgNn1vqDZAkEAvBFt/ERW1UnV6fwOTa9x6yxNVNpd3tKRD4li+u0x
oAvGVHdn+B1JJBkTJccu9hOAWjyXX5C2QuuC/fNKmsqxyQ==
-----END RSA PRIVATE KEY-----
    """

    return conf


@pytest.yield_fixture(scope="function")
def app(loop, pg_server, config):
    config.db.host = pg_server["params"]["host"]
    config.db.port = pg_server["params"]["port"]
    config.db.user = pg_server["params"]["user"]
    config.db.password = pg_server["params"]["password"]
    config.db.database = pg_server["params"]["database"]

    app = loop.run_until_complete(init("wallet", config))
    runner = web.AppRunner(app)

    cwd = Path(os.path.dirname(__file__))
    sql_root = cwd / ".." / "src" / "wallet" / "storage" / "sql"

    cmd = "cat {schema} | PGPASSWORD='{password}' psql -h {host} -p {port} -d {database} -U {user}"  # noqa

    subprocess.call(
        [
            cmd.format(
                schema=(sql_root / "upgrade_schema.sql").as_posix(),
                host=config.db.host,
                port=config.db.port,
                user=config.db.user,
                password=config.db.password,
                database=config.db.database,
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
                host=config.db.host,
                port=config.db.port,
                user=config.db.user,
                password=config.db.password,
                database=config.db.database,
            )
        ],
        shell=True,
        cwd=cwd.as_posix(),
    )


@pytest.fixture(scope="session")
def fake():
    return faker.Faker()


@pytest.fixture(scope="session")
def today():
    return pendulum.today()


@pytest.fixture(scope="session")
def month(today):
    return today.start_of("month").date()


@pytest.fixture(scope="function")
def user(fake: Any) -> User:
    return User(key=1, email=fake.free_email())
