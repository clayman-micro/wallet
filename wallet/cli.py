import asyncio

import click

from wallet.app import create_app, create_config, destroy_app
from wallet.management.db import db


class Context(object):

    def __init__(self, config):
        self.loop = asyncio.get_event_loop()
        conf = create_config(config)
        self.instance = self.loop.run_until_complete(create_app(conf,
                                                                self.loop))


@click.group()
@click.option('-c', '--config', default='config.json')
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

    handler = app.make_handler()
    f = context.loop.create_server(handler, host, port)
    srv = context.loop.run_until_complete(f)

    print('Application serving on %s' % str(srv.sockets[0].getsockname()))

    try:
        context.loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.sockets[0].close()
        context.loop.run_until_complete(destroy_app(app))
        context.loop.run_until_complete(handler.finish_connections())
        context.loop.run_until_complete(app.finish())
        context.loop.close()


cli.add_command(db, name='db')
