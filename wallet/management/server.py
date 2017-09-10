import asyncio  # noqa
import socket

import click
import ujson
from aiohttp import ClientSession

from wallet import App


async def register_service(app: App) -> str:
    service_name = '_'.join((
        app.config.get('app_name'), app.config.get('app_hostname')
    ))
    payload = {
        'ID': service_name,
        'NAME': app.config.get('app_name'),
        'Tags': ['master', 'v1'],
        'Address': app.config.get('app_host'),
        'Port': app.config.get('app_port')
    }

    url = 'http://{host}:{port}/v1/agent/service/register'.format(
        host=app.config.get('consul_host'), port=app.config.get('consul_port'))

    with ClientSession() as session:
        async with session.put(url, data=ujson.dumps(payload)) as resp:
            assert resp.status == 200

    app.logger.info('Register service "%s"' % service_name)

    return service_name


async def unregister_service(service_name: str, app: App):
    if service_name:
        url = 'http://{host}:{port}/v1/agent/service/deregister/{id}'.format(
            id=service_name,
            host=app.config.get('consul_host'),
            port=app.config.get('consul_port')
        )

        with ClientSession() as session:
            async with session.get(url) as resp:
                assert resp.status == 200

        app.logger.info('Remove service "%s" from Consul' % service_name)


@click.group()
@click.pass_obj
def server(context):
    context.instance = context.loop.run_until_complete(
        context.init_app(context.conf, context.logger, context.loop)
    )


@server.command()
@click.option('--host', default='127.0.0.1', help='Specify application host.')
@click.option('--port', default=5000, help='Specify application port.')
@click.option('--consul', is_flag=True, default=False)
@click.pass_obj
def run(context, host, port, consul):
    """ Run application instance. """

    app = context.instance  # type: App
    loop = context.loop  # type: asyncio.BaseEventLoop

    handler = app.make_handler(access_log=context.logger,
                               access_log_format=app.config.get('access_log'))
    srv = loop.run_until_complete(loop.create_server(handler, host, port))

    if 'app_host' not in app.config:
        try:
            ip_address = socket.gethostbyname(app.config.get('app_hostname'))
        except socket.gaierror:
            ip_address = '127.0.0.1'

        app.config['app_host'] = ip_address

    app.config['app_port'] = int(port)

    service_name = None
    if consul:
        service_name = loop.run_until_complete(register_service(app))

    loop.run_until_complete(app.startup())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if consul and service_name:
            loop.run_until_complete(unregister_service(service_name, app))

        srv.close()
        loop.run_until_complete(srv.wait_closed())

        loop.run_until_complete(app.shutdown())
        loop.run_until_complete(handler.finish_connections(60))
        loop.run_until_complete(app.cleanup())

    loop.close()
