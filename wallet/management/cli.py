import asyncio
import logging
import logging.config

import click
import uvloop

from wallet import configure, init
from wallet.management.server import server


class Context(object):

    def __init__(self, config):
        self.conf = configure(config, {
            'app_name': 'wallet',

            'secret_key': 'secret',

            'db_name': 'wallet',
            'db_user': 'wallet',
            'db_password': 'wallet'
        })
        self.init_app = init

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop = asyncio.get_event_loop()

        logging.config.dictConfig(self.conf['logging'])

        self.logger = logging.getLogger('app')


@click.group()
@click.option('-c', '--config', default='config.yml')
@click.pass_context
def cli(context, config: str):
    context.obj = Context(config)


cli.add_command(server, name='server')
