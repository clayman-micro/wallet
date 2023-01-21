import socket

import click
from aiohttp import web


def get_address(default: str = "127.0.0.1") -> str:
    """Get current host IP-address.

    Args:
        default: Default IP-address.

    Returns:
        IP-address.
    """
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 1))
            ip_address = s.getsockname()[0]
        except socket.gaierror:
            ip_address = default
        finally:
            s.close()

    return ip_address


@click.group()
@click.pass_context
def server(ctx: click.Context) -> None:
    """Server commands group.

    Args:
        ctx: Current context.
    """


@server.command()
@click.option("--host", default=None, help="Specify application host")
@click.option("--port", default=5000, type=int, help="Specify application port")
@click.pass_context
def run(ctx: click.Context, host: str, port: int) -> None:
    """Run server instance.

    Args:
        ctx: Current context.
        host: Application host.
        port: Application port.
    """
    app: web.Application = ctx.obj["app"]

    if port < 1024 and port > 65535:
        raise RuntimeError("Port should be from 1024 to 65535")

    if not host:
        host = "127.0.0.1"
        address = "127.0.0.1"
    else:
        address = get_address()

    app.logger.info(f"Application serving on http://{address}:{port}")

    web.run_app(
        app,
        host=host,
        port=port,
        access_log=app.logger.bind(context="access"),  # type: ignore
        access_log_format="%r",
        print=lambda foo: None,
    )

    app.logger.info("Shutdown application")
