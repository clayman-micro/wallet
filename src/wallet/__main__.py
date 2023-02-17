import click
import pkg_resources
import uvloop

from wallet.app import create_container, init
from wallet.cli.server import server
from wallet.logging import configure_logging


@click.group()
@click.option("--debug", is_flag=True, default=False, envvar="DEBUG")
@click.pass_context
def cli(ctx: click.Context, debug: bool = False) -> None:
    """Prepare application entry point for command line interface.

    Args:
        ctx: Current command line application context.
        debug: Run application in debug mode.
    """
    dist = pkg_resources.get_distribution("wallet")

    logger = configure_logging(dist=dist, debug=debug)

    ctx.obj["app"] = init(dist=dist, container=create_container(logger=logger), debug=debug)


cli.add_command(server, name="server")


if __name__ == "__main__":
    uvloop.install()

    cli(obj={})
