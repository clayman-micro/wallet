import asyncio

import click
import uvloop  # type: ignore
from aiohttp_micro.management.server import server  # type: ignore
from aiohttp_storage.management.storage import storage  # type: ignore
from config import (  # type: ignore
    ConsulConfig,
    EnvValueProvider,
    load,
)

from wallet.app import AppConfig, init
from wallet.cli.accounts import accounts


@click.group()
@click.option("--debug", is_flag=True, default=False)
@click.pass_context
def cli(ctx, debug: bool = False) -> None:
    uvloop.install()
    loop = asyncio.get_event_loop()

    consul_config = ConsulConfig()
    load(consul_config, providers=[EnvValueProvider()])

    config = AppConfig(
        defaults={
            "consul": consul_config,
            "debug": debug,
            "db": {
                "user": "wallet",
                "password": "wallet",
                "database": "wallet",
            },
        }
    )
    load(config, providers=[EnvValueProvider()])

    app = init("wallet", config)

    ctx.obj["app"] = app
    ctx.obj["config"] = config
    ctx.obj["loop"] = loop


cli.add_command(server, name="server")
cli.add_command(storage, name="storage")

cli.add_command(accounts, name="accounts")


if __name__ == "__main__":
    cli(obj={})
