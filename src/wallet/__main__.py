import click
import uvloop

from wallet.app import init
from wallet.cli.server import server


@click.group()
@click.option("--debug", is_flag=True, default=False)
@click.pass_context
def cli(ctx: click.Context, debug: bool = False) -> None:
    """Main application entry point for command line interface.

    Args:
        ctx: Current command line application context.
        debug: Run application in debug mode.
    """
    ctx.obj["app"] = init("wallet", debug=debug)


cli.add_command(server, name="server")


if __name__ == "__main__":
    uvloop.install()

    cli(obj={})
