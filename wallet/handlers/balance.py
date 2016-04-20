import functools
from datetime import datetime
from typing import Dict

import sqlalchemy
from aiohttp import web

from wallet.utils.handlers import register_handler
from ..exceptions import ResourceNotFound
from ..storage import accounts, balance
from . import base, auth


def account_required(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        """ Check that account exists and access granted"""

        request = args[-1]  # type web.Request
        owner = kwargs.get('owner')  # type: Dict

        account_id = base.get_instance_id(request, 'account_id')
        async with request.app['engine'].acquire() as conn:
            try:
                account = await accounts.get_account(account_id, owner, conn)
            except ResourceNotFound:
                raise web.HTTPNotFound(text='Account not found')
            else:
                kwargs['account'] = account

        return await f(*args, **kwargs)
    return wrapper


def serialize(value):
    return {
        'income': float(value['income']),
        'expense': float(value['expense']),
        'remain': float(value['remain']),
        'date': datetime.strftime(value['date'], '%Y-%m-%dT%H:%M:%S')
    }


@auth.owner_required
@account_required
@base.handle_response
async def get_balance(request: web.Request, account: Dict, owner: Dict) -> Dict:
    collection = []
    async with request.app['engine'].acquire() as conn:
        query = sqlalchemy.select([balance.table]).where(
            balance.table.c.account_id == account.get('id')
        )
        async for row in conn.execute(query):
            item = dict(zip(row.keys(), row.values()))
            collection.append(serialize(item))

    return {
        'balance': collection,
        'meta': {
            'account': {
                'id': account.get('id')
            }
        }
    }


@auth.owner_required
@account_required
@base.handle_response
async def update_balance(request: web.Request, account: Dict, owner: Dict):
    async with request.app['engine'].aqcuire() as conn:
        today = datetime.today()
        account_balance = await accounts.calculate_balance(account, today, conn)
        await balance.update_balance(account_balance, account, conn)

    return {
        'balance': list(map(serialize, account_balance)),
        'meta': {
            'account': {
                'id': account.get('id')
            }
        }
    }


def register(app, url_prefix, name_prefix):
    with register_handler(app, url_prefix, name_prefix) as register:
        register('GET', 'balance', get_balance, 'get_balance')
        register('PUT', 'balance', update_balance, 'update_balance')
