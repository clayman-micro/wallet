import socket

import click
import ujson
from aiohttp import ClientSession, web


async def register_service(app: web.Application) -> str:
    config = app["config"]

    service_name = f"{config['app_name']}_{config['app_hostname']}"
    host = config["app_host"]
    port = config["app_port"]

    payload = {
        "ID": service_name,
        "NAME": config["app_name"],
        "Tags": ["master"],
        "Address": host,
        "Port": port,
        "Check": {"HTTP": f"http://{host}:{port}/-/health", "Interval": "10s"},
    }

    url = "http://{host}:{port}/v1/agent/service/register".format(
        host=config["consul_host"], port=config["consul_port"]
    )

    async with ClientSession() as session:
        async with session.put(url, data=ujson.dumps(payload)) as resp:
            assert resp.status == 200

    app.logger.info('Register service "%s"' % service_name)

    return service_name


async def unregister_service(service_name: str, app: web.Application) -> None:
    config = app["config"]

    if service_name:
        url = "http://{host}:{port}/v1/agent/service/deregister/{id}".format(
            id=service_name, host=config["consul_host"], port=config["consul_port"]
        )

        async with ClientSession() as session:
            async with session.put(url) as resp:
                assert resp.status == 200

        app.logger.info('Remove service "%s" from Consul' % service_name)


@click.group()
@click.pass_obj
def server(context):
    context.instance = context.loop.run_until_complete(
        context.init_app(context.conf, context.logger)
    )


@server.command()
@click.option("--host", default="127.0.0.1", help="Specify application host.")
@click.option("--port", default=5000, help="Specify application port.")
@click.option("--consul", is_flag=True, default=False)
@click.pass_obj
def run(context, host, port, consul):
    """ Run application instance. """

    app = context.instance
    loop = context.loop

    runner = web.AppRunner(
        app,
        handle_signals=True,
        access_log=context.logger,
        access_log_format=app["config"]["access_log"],
    )

    try:
        ip_address = socket.gethostbyname(app["config"]["app_hostname"])
    except socket.gaierror:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 1))
            ip_address = s.getsockname()[0]
        except socket.gaierror:
            ip_address = host
        finally:
            s.close()

    app["config"]["app_host"] = ip_address
    app["config"]["app_port"] = int(port)

    service_name = None
    if consul:
        service_name = loop.run_until_complete(register_service(app))

    loop.run_until_complete(runner.setup())

    try:
        site = web.TCPSite(runner, app["config"]["app_host"], port)
        loop.run_until_complete(site.start())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if consul and service_name:
            loop.run_until_complete(unregister_service(service_name, app))

        loop.run_until_complete(runner.cleanup())

    loop.close()
