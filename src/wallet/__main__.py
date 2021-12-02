import asyncio

import click
import uvloop  # type: ignore
from aiohttp_micro.cli.server import server  # type: ignore
from aiohttp_storage.management.storage import storage  # type: ignore
from config import EnvValueProvider, load  # type: ignore

from wallet.app import init
from wallet.config import AppConfig, VaultConfig, VaultProvider


@click.group()
@click.option("--debug", is_flag=True, default=False)
@click.pass_context
def cli(ctx, debug: bool = False) -> None:
    uvloop.install()
    loop = asyncio.get_event_loop()

    vault_config = VaultConfig()
    load(vault_config, providers=[EnvValueProvider()])

    config = AppConfig(defaults={"debug": debug, "db": {"user": "wallet", "password": "wallet", "database": "wallet"}})
    load(config, providers=[VaultProvider(config=vault_config, mount_point="credentials"), EnvValueProvider()])

    app = init("wallet", config)

    if config.debug:
        app["logger"].debug("Application config", db=config.db.uri, sentry=config.sentry_dsn)

    ctx.obj["app"] = app
    ctx.obj["config"] = config
    ctx.obj["loop"] = loop


cli.add_command(server, name="server")
cli.add_command(storage, name="storage")


if __name__ == "__main__":
    cli(obj={})
