import asyncio

import click

from wallet import Application
from wallet.management.db import db


class Context(object):

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.instance = Application(loop=self.loop)
        self.loop.run_until_complete(self.instance.configure())


@click.group()
@click.pass_context
def cli(context):
    """ Experimental application

    :param context: Click context object
    """

    context.obj = Context()


@cli.command()
@click.option('--host', default='127.0.0.1', help='Specify application host.')
@click.option('--port', default='5000', help='Specify application port.')
@click.pass_obj
def run(context, host, port):
    """ Run application instance. """

    app = context.instance

    f = context.loop.create_server(app.make_handler(), host, port)
    srv = context.loop.run_until_complete(f)

    print('Application serving on {}'.format(srv.sockets[0].getsockname()))

    try:
        context.loop.run_forever()
    except KeyboardInterrupt:
        context.loop.run_until_complete(app.close())
        context.loop.close()


cli.add_command(db, name='db')
