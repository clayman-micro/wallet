import asyncio
import functools
import logging
import logging.config
import signal
import socket

import click

from wallet.app import create_config, init, register_service
from wallet.management.db import db


class Context(object):

    def __init__(self, config):
        self.loop = asyncio.get_event_loop()
        conf = create_config(config)

        logging.config.dictConfig(conf['logging'])

        self.logger = logging.getLogger('wallet')
        self.instance = self.loop.run_until_complete(init(conf, self.logger,
                                                          self.loop))


def shutdown(app, loop):
    loop.stop()


@click.group()
@click.option('-c', '--config', default='config.yml')
@click.pass_context
def cli(context, config):
    """ Experimental application

    :param context: Click context object
    """
    context.obj = Context(config)


@cli.command()
@click.option('--host', default='127.0.0.1', help='Specify application host.')
@click.option('--port', default='5000', help='Specify application port.')
@click.pass_obj
def run(context, host, port):
    """ Run application instance. """

    app = context.instance
    loop = context.loop

    handler = app.make_handler(access_log=context.logger,
                               access_log_format=app['config']['ACCESS_LOG'])
    srv = loop.run_until_complete(loop.create_server(handler, host, port))

    hostname = socket.gethostname()
    app['config']['APP_HOSTNAME'] = hostname

    if 'APP_ADDRESS' not in app['config']:
        try:
            ip_addr = socket.gethostbyname(hostname)
        except socket.gaierror:
            ip_addr = srv.sockets[0].getsockname()[0]

        app['config']['APP_ADDRESS'] = ip_addr

    app['config']['APP_PORT'] = int(port)

    app.logger.info('Application serving on %s:%s' % (
        app['config']['APP_ADDRESS'], app['config']['APP_PORT']))

    loop.run_until_complete(register_service(app))

    for signame in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, signame),
                                functools.partial(shutdown, app, loop))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.close()
        loop.run_until_complete(srv.wait_closed())
        loop.run_until_complete(app.shutdown())
        loop.run_until_complete(handler.finish_connections(60))
        loop.run_until_complete(app.cleanup())
    loop.close()


cli.add_command(db, name='db')
