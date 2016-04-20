from functools import wraps
from decimal import Decimal
from typing import Dict

import sqlalchemy
from aiohttp import web
from aiopg.sa import Engine
from sqlalchemy import and_, func, select

from wallet.utils.handlers import register_handler
from ..handlers import auth, base
from ..storage import accounts, details, transactions
from ..storage.base import to_decimal, create_instance


schema = {
    'id': {
        'type': 'integer'
    },
    'name': {
        'type': 'string',
        'maxlength': 255,
        'required': True
    },
    'price_per_unit': {
        'type': 'decimal',
        'coerce': to_decimal(2),
        'required': True,
    },
    'count': {
        'type': 'decimal',
        'coerce': to_decimal(3),
        'required': True,
    },
    'total': {
        'type': 'decimal',
        'coerce': to_decimal(2),
    },
    'transaction_id': {
        'type': 'integer',
        'coerce': int
    }
}


def serialize(value):
    return {
        'id': value['id'],
        'name': value['name'],
        'price_per_unit': round(float(value['price_per_unit']), 2),
        'count': round(float(value['count']), 3),
        'total': round(float(value['total']), 2),
        'transaction_id': value['transaction_id']
    }


def transaction_required(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        """ Check that transaction exists and it's owner match owner """

        request = args[-1]  # type: web.Request
        owner = kwargs.get('owner')  # type: Dict

        transaction_id = base.get_instance_id(request, 'transaction_id')

        table = transactions.table
        query = select([transactions.table]).select_from(
                sqlalchemy.join(table, accounts.table,
                                accounts.table.c.id == table.c.account_id)
            ).where(and_(accounts.table.c.id == owner.get('id'),
                         table.c.id == transaction_id))

        transaction = {}
        async with request.app['engine'].acquire() as conn:
            result = await conn.execute(query)

            if result.returns_rows and result.rowcount == 1:
                row = await result.fetchone()
                transaction = dict(zip(row.keys(), row.values()))
            else:
                raise web.HTTPNotFound

        kwargs['transaction'] = transaction
        return await f(*args, **kwargs)
    return wrapper


@auth.owner_required
@transaction_required
@base.handle_response
async def get_details(request: web.Request, owner: Dict, transaction: Dict):
    collection = []

    table = transactions.table
    join = sqlalchemy.join(table, details.table,
                           table.c.id == details.table.c.transaction_id)
    params = (table.c.id == transaction.get('id'), )

    async with request.app['engine'].acquire() as conn:
        query = select([details.table]).select_from(join).where(*params)
        async for item in conn.execute(query):
            collection.append(item)

        total = await conn.scalar(select([func.count()]).select_from(
            details.table).select_from(join).where(*params))

    return {
        'details': list(map(serialize, collection)),
        'meta': {
            'count': len(collection),
            'total': total
        }
    }


@auth.owner_required
@transaction_required
@base.handle_response
async def create_detail(request: web.Request, owner: Dict, transaction: Dict):
    payload = await base.get_payload(request)
    document = base.validate_payload(payload, schema)
    document['transaction_id'] = transaction['id']
    if 'total' not in document:
        total = document['price_per_unit'] * document['count']
        document['total'] = Decimal(total).quantize(Decimal('0.01'))

    async with request.app['engine'].acquire() as conn:
        resource = await create_instance(document, details.table, conn)

    return base.json_response({
        'detail': serialize(resource),
    }, status=201)


@auth.owner_required
@transaction_required
@base.handle_response
async def get_detail(request: web.Request, owner: Dict, transaction: Dict):
    instance_id = base.get_instance_id(request)
    async with request.app['engine'].acquire() as conn:
        detail = await details.get_detail(instance_id, transaction, conn)
    return {'detail': serialize(detail)}


@auth.owner_required
@transaction_required
@base.handle_response
async def update_detail(request: web.Request, owner: Dict, transaction: Dict):
    instance_id = base.get_instance_id(request)

    async with request.app['engine'].acquire() as conn:
        detail = await details.get_detail(instance_id, transaction, conn)

        payload = await base.get_payload(request)
        document = base.validate_payload(payload, schema, update=True)
        detail.update(document)

        total = detail['price_per_unit'] * detail['count']
        detail['total'] = Decimal(total).quantize(Decimal('0.01'))

        after = await base.update_instance(detail, details.table, conn)

    return {'detail': serialize(after)}


@auth.owner_required
@transaction_required
@base.handle_response
async def remove_detail(request: web.Request, owner: Dict, transaction: Dict):
    instance_id = base.get_instance_id(request)

    async with request.app['engine'].acquire() as conn:
        detail = await details.get_detail(instance_id, transaction, conn)
        await base.remove_instance(detail, details.table, conn)

    return {'detail': 'removed'}


def register(app, url_prefix, name_prefix):
    with register_handler(app, url_prefix, name_prefix) as register:
        register('GET', '', get_details, 'get_details')
        register('POST', '', create_detail, 'create_detail')
        register('GET', '{instance_id}', get_detail, 'get_detail')
        register('PUT', '{instance_id}', update_detail, 'update_detail')
        register('DELETE', '{instance_id}', remove_detail, 'remove_detail')
