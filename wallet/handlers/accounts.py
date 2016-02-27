from datetime import datetime
from typing import Dict

import sqlalchemy
from aiohttp import web

from wallet.storage.base import to_decimal
from wallet.utils.handlers import register_handler
from ..exceptions import ValidationError
from ..storage import accounts, balance as balance_storage
from . import base, auth


schema = {
    'id': {
        'type': 'integer',
    },
    'name': {
        'type': 'string',
        'maxlength': 255,
        'required': True,
        'empty': False
    },
    'original_amount': {
        'type': 'decimal',
        'coerce': to_decimal(2),
        'empty': True
    },
    'created_on': {
        'type': 'datetime',
        'empty': True
    },
    'owner_id': {
        'type': 'integer',
        'coerce': int,
        'readonly': True
    }
}


async def validate(document, request, owner, resource=None):
    params = [
        accounts.table.c.name == document.get('name'),
        accounts.table.c.owner_id == owner.get('id')
    ]

    if resource is not None:
        params.append(accounts.table.c.id != resource.get('id'))

    async with request.app['engine'].acquire() as conn:
        count = await conn.scalar(
            sqlalchemy.select([sqlalchemy.func.count()])
                .select_from(accounts.table)
                .where(sqlalchemy.and_(*params)))
        if count > 0:
            raise ValidationError({'name': 'Already exists.'})

    if not resource:
        document.setdefault('owner_id', owner.get('id'))
        document.setdefault('created_on', datetime.now())

    return document


def serialize(resource):
    balance = resource.get('balance')  # type: Dict

    return {
        'id': resource['id'],
        'name': resource['name'],
        'balance': {
            'income': float(balance['income']),
            'expense': float(balance['expense']),
            'remain': float(balance['remain']),
        }
    }


@auth.owner_required
@base.handle_response
async def get_accounts(request: web.Request, owner: Dict) -> Dict:
    collection = []

    params = accounts.table.c.owner_id == owner.get('id')
    async with request.app['engine'].acquire() as conn:
        async for account in conn.execute(accounts.get_account_query(params)):
            collection.append({
                'id': account.id,
                'name': account.name,
                'balance': {
                    'income': account.income,
                    'expense': account.expense,
                    'remain': account.remain
                }
            })

        total = await conn.scalar(
            sqlalchemy.select([sqlalchemy.func.count()])
                .select_from(accounts.table)
                .where(params)
        )

    return {
        'accounts': collection,
        'meta': {
            'count': len(collection),
            'total': total
        }
    }


@auth.owner_required
@base.create_handler('account', accounts.table, schema, validate, serialize)
async def create_account(account, request: web.Request, owner: Dict) -> Dict:
    engine = request.app['engine']
    balance = await accounts.calculate_balance(account, engine)
    await balance_storage.update_balance(balance, account, engine=engine)
    account['balance'] = balance[-1]
    return account


@auth.owner_required
@base.handle_response
async def get_account(request: web.Request, owner: Dict) -> Dict:
    instance_id = base.get_instance_id(request)
    account = await accounts.get_account(instance_id, owner,
                                         engine=request.app['engine'])
    return {'account': serialize(account)}


@auth.owner_required
@base.handle_response
async def update_account(request: web.Request, owner: Dict) -> Dict:
    instance_id = base.get_instance_id(request)

    # Get resource
    account = await accounts.get_account(instance_id, owner,
                                         engine=request.app['engine'])

    # Validate payload
    payload = await base.get_payload(request)
    document = base.validate_payload(payload, schema, update=True)

    # Validate resource after update
    before = account.copy()
    account.update(document)
    resource = await validate(account, request, owner, resource=account)

    # Update resource
    balance = resource.pop('balance')
    after = await base.update_instance(resource, accounts.table,
                                       request.app['engine'])
    after['balance'] = balance

    # Update balance
    if before['original_amount'] != after['original_amount']:
        engine = request.app['engine']
        balance = await accounts.calculate_balance(after, engine=engine)
        await balance_storage.update_balance(balance, after, engine=engine)
        after['balance'] = balance[-1]

    return {'account': serialize(after)}


@auth.owner_required
@base.handle_response
async def remove_account(request: web.Request, owner: Dict) -> Dict:
    instance_id = base.get_instance_id(request)
    engine = request.app['engine']

    account = await accounts.get_account(instance_id, owner, engine=engine)
    await base.remove_instance(account, accounts.table, engine=engine)

    return {'account': 'removed'}


def register(app):
    with register_handler(app, '/api/accounts', 'api') as register:
        register('GET', '', get_accounts, 'get_accounts')
        register('POST', '', create_account, 'create_account')
        register('GET', '{instance_id}', get_account, 'get_account')
        register('PUT', '{instance_id}', update_account, 'update_account')
        register('DELETE', '{instance_id}', remove_account, 'remove_account')
