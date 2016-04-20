from datetime import datetime
from typing import Dict

import sqlalchemy
from aiohttp import web
from aiopg.sa import SAConnection

from wallet.utils.handlers import register_handler
from ..exceptions import ValidationError
from ..storage import accounts, balance as balance_storage, categories, transactions
from ..storage.base import to_decimal, to_datetime
from . import base, auth


schema = {
    'id': {
        'type': 'integer'
    },
    'type': {
        'type': 'string',
        'maxlength': 20,
        'required': True,
        'empty': False,
        'allowed': transactions.TRANSACTION_TYPES
    },
    'description': {
        'type': 'string',
        'maxlength': 255,
        'empty': True
    },
    'amount': {
        'type': 'decimal',
        'coerce': to_decimal(2),
        'required': True,
        'empty': False
    },
    'account_id': {
        'type': 'integer',
        'coerce': int,
        'required': True,
        'empty': False
    },
    'category_id': {
        'type': 'integer',
        'coerce': int,
        'required': True,
        'empty': False
    },
    'created_on': {
        'type': 'datetime',
        'coerce': to_datetime,
        'empty': True
    }
}


async def validate(document, request, owner, resource=None):
    async with request.app['engine'].acquire() as conn:
        count = await conn.scalar(
            sqlalchemy.select([sqlalchemy.func.count()])
                .select_from(accounts.table)
                .where(sqlalchemy.and_(
                    accounts.table.c.id == document.get('account_id'),
                    accounts.table.c.owner_id == owner.get('id'),
                )))
        if not count:
            raise ValidationError({'account_id': 'Account does not exists'})

        count = await conn.scalar(
            sqlalchemy.select([sqlalchemy.func.count()])
                .select_from(categories.table)
                .where(sqlalchemy.and_(
                    categories.table.c.id == document.get('category_id'),
                    categories.table.c.owner_id == owner.get('id')
                )))
        if not count:
            raise ValidationError({'category_id': 'Category does not exists'})

    if not resource:
        document.setdefault('created_on', datetime.now())

    return document


def serialize(value):
    return {
        'id': value['id'],
        'type': value['type'],
        'description': value['description'],
        'amount': float(value['amount']),
        'account_id': value['account_id'],
        'category_id': value['category_id'],
        'created_on': datetime.strftime(value['created_on'], '%Y-%m-%dT%H:%M:%S')
    }


async def update_balance(account_id: int, owner_id: int, conn: SAConnection):
    query = sqlalchemy.select([accounts.table]).where(sqlalchemy.and_(
        accounts.table.c.id == account_id,
        accounts.table.c.owner_id == owner_id
    ))
    account = await base.get_instance(query, conn=conn)
    today = datetime.today()

    balance = await accounts.calculate_balance(account, today, conn=conn)
    await balance_storage.update_balance(balance, account, conn=conn)


@auth.owner_required
@base.handle_response
async def get_transactions(request: web.Request, owner: Dict) -> Dict:
    collection = []

    table = transactions.table
    join = sqlalchemy.join(table, accounts.table,
                           accounts.table.c.id == table.c.account_id)
    params = accounts.table.c.owner_id == owner.get('id')
    query = sqlalchemy.select([table]).select_from(join).where(
        params).order_by(table.c.created_on.desc())

    async with request.app['engine'].acquire() as conn:
        async for transaction in conn.execute(query):
            collection.append(transaction)

        total = await conn.scalar(
            sqlalchemy.select([sqlalchemy.func.count()])
                .select_from(table)
                .select_from(join)
                .where(params)
        )

    return {
        'transactions': list(map(serialize, collection)),
        'meta': {
            'count': len(collection),
            'total': total
        }
    }


@auth.owner_required
@base.create_handler('transaction', transactions.table, schema, validate, serialize)
async def create_transaction(transaction, request: web.Request, owner: Dict):
    async with request.app['engine'].acquire() as conn:
        await update_balance(transaction.get('account_id'), owner.get('id'),
                             conn)
    return transaction


@auth.owner_required
@base.handle_response
async def get_transaction(request: web.Request, owner: Dict) -> Dict:
    instance_id = base.get_instance_id(request)
    async with request.app['engine'].acquire() as conn:
        transaction = await transactions.get_transaction(instance_id, owner, conn)
    return {'transaction': serialize(transaction)}


@auth.owner_required
@base.handle_response
async def update_transaction(request: web.Request, owner: Dict) -> Dict:
    instance_id = base.get_instance_id(request)

    async with request.app['engine'].acquire() as conn:
        # Get resource
        transaction = await transactions.get_transaction(instance_id, owner,
                                                         conn=conn)

        # Validate payload
        payload = await base.get_payload(request)
        document = base.validate_payload(payload, schema, update=True)

        # Validate resource after update
        before = transaction.copy()
        transaction.update(document)
        resource = await validate(transaction, request, owner, transaction)

        # Update resource
        after = await base.update_instance(resource, transactions.table, conn)

        # Update account balance if needed
        if before['amount'] != after['amount'] or before['type'] != after['type']:
            await update_balance(transaction.get('account_id'), owner.get('id'),
                                 conn)

    return {'transaction': serialize(after)}


@auth.owner_required
@base.handle_response
async def remove_transaction(request: web.Request, owner: Dict) -> Dict:
    instance_id = base.get_instance_id(request)

    async with request.app['engine'].acquire() as conn:
        transaction = await transactions.get_transaction(instance_id, owner, conn)
        await base.remove_instance(transaction, transactions.table, conn)

        # Update account balance
        await update_balance(transaction.get('account_id'), owner.get('id'), conn)

    return {'transaction': 'removed'}


def register(app, url_prefix, name_prefix):
    with register_handler(app, url_prefix, name_prefix) as register:
        register('GET', '', get_transactions, 'get_transactions')
        register('POST', '', create_transaction, 'create_transaction')
        register('GET', '{instance_id}', get_transaction, 'get_transaction')
        register('PUT', '{instance_id}', update_transaction,
                 'update_transaction')
        register('DELETE', '{instance_id}', remove_transaction,
                 'remove_transaction')
