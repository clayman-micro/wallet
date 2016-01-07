from aiohttp import web
from functools import wraps
import sqlalchemy
from decimal import Decimal
from sqlalchemy import and_, func, select
from typing import Dict

from ..handlers import auth, base
from ..storage import accounts, details, transactions
from ..utils.db import Connection


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
        async with Connection(request.app['engine']) as conn:
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
@base.get_collection('details', serialize=details.serialize)
async def get_details(request: web.Request, **kwargs):
    transaction = kwargs.get('transaction')
    table = transactions.table
    join = sqlalchemy.join(table, details.table,
                           table.c.id == details.table.c.transaction_id)
    params = (table.c.id == transaction.get('id'), )

    query = select([details.table]).select_from(join).where(*params)
    total_query = select([func.count()]).select_from(
        details.table).select_from(join).where(*params)

    return query, total_query


class DetailResourceHandler(base.ResourceHandler):
    decorators = (transaction_required, auth.owner_required,
                  base.handle_response)

    resource_name = 'detail'

    table = details.table
    schema = details.schema

    def serialize(self, resource):
        return details.serialize(resource)

    def get_resource_query(self, request: web.Request, **kwargs):
        table = transactions.table
        transaction = kwargs.get('transaction')

        return select([self.table]).select_from(sqlalchemy.join(
            table, self.table, table.c.id == self.table.c.transaction_id)
        ).where(and_(
            table.c.id == transaction.get('id'),
            self.table.c.id == base.get_instance_id(request)
        ))

    async def validate(self, document: Dict, request: web.Request, **kwargs):
        instance = kwargs.get('instance', None)
        transaction = kwargs.get('transaction')  # type: Dict

        total = document['price_per_unit'] * document['count']
        document['total'] = Decimal(total).quantize(Decimal('0.01'))

        if not instance:
            document.setdefault('transaction_id', transaction.get('id'))

        return document
