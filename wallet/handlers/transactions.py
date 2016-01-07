from datetime import datetime
from decimal import Decimal

from aiohttp import web
import sqlalchemy
from sqlalchemy import and_, func, select
from typing import Dict

from ..exceptions import ValidationError
from ..storage import accounts, categories, transactions
from ..utils.db import Connection
from . import base, auth


@auth.owner_required
@base.get_collection('transactions', serialize=transactions.serialize)
async def get_transactions(request: web.Request, **kwargs) -> tuple:
    owner = kwargs.get('owner')
    table = transactions.table

    join = sqlalchemy.join(table, accounts.table,
                           accounts.table.c.id == table.c.account_id)
    params = (accounts.table.c.owner_id == owner.get('id'), )

    query = select([table]).select_from(join).where(
        *params).order_by(table.c.created_on.desc())
    total_query = select([func.count()]).select_from(table).select_from(
        join).where(*params)

    return query, total_query


class TransactionResourceHandler(base.ResourceHandler):
    decorators = (auth.owner_required, base.handle_response)

    resource_name = 'transaction'

    table = transactions.table
    schema = transactions.schema

    def serialize(self, resource):
        return transactions.serialize(resource)

    def get_resource_query(self, request: web.Request, **kwargs):
        owner = kwargs.get('owner')

        instance_id = base.get_instance_id(request)

        join = sqlalchemy.join(self.table, accounts.table,
                               accounts.table.c.id == self.table.c.account_id)
        return select([self.table]).select_from(join).where(and_(
            self.table.c.id == instance_id,
            accounts.table.c.owner_id == owner.get('id')
        ))

    async def validate(self, document: Dict, request: web.Request, **kwargs):
        owner = kwargs.get('owner')
        instance = kwargs.get('instance', None)

        async with Connection(request.app['engine']) as conn:
            query = select([func.count()]).select_from(accounts.table).where(and_(
                accounts.table.c.id == document.get('account_id'),
                accounts.table.c.owner_id == owner.get('id'),
            ))
            count = await conn.scalar(query)
            if not count:
                raise ValidationError({'account_id': 'Account does not exists'})

            query = select([func.count()]).select_from(categories.table).where(
                categories.table.c.id == document.get('category_id')
            )
            count = await conn.scalar(query)
            if not count:
                raise ValidationError({'category_id': 'Category does not exists'})

        if not instance:
            document.setdefault('created_on', datetime.now())

        return document

    async def after_create(self, resource, request: web.Request, **kwargs):
        # Update account after creation
        table = accounts.table

        async with Connection(request.app['engine']) as conn:
            query = select([table.c.current_amount, ]).where(
                table.c.id == resource['account_id'])
            current_amount = await conn.scalar(query)

            if resource['type'] == transactions.INCOME_TRANSACTION:
                current_amount = current_amount + Decimal(resource['amount'])
            elif resource['type'] == transactions.EXPENSE_TRANSACTION:
                current_amount = current_amount - Decimal(resource['amount'])

            await conn.execute(table.update().where(
                table.c.id == resource['account_id']).values(
                    current_amount=current_amount.quantize(Decimal('.01'))))

    async def after_update(self, resource, request: web.Request, **kwargs):
        before = kwargs.get('before')
        table = accounts.table

        async with Connection(request.app['engine']) as conn:
            query = select([table.c.current_amount, ]).where(
                table.c.id == resource['account_id'])
            current_amount = await conn.scalar(query)

            if before['type'] == transactions.INCOME_TRANSACTION:
                current_amount = current_amount - before['amount']
            elif before['type'] == transactions.EXPENSE_TRANSACTION:
                current_amount = current_amount + before['amount']

            if resource['type'] == transactions.INCOME_TRANSACTION:
                current_amount = current_amount + Decimal(resource['amount'])
            elif resource['type'] == transactions.EXPENSE_TRANSACTION:
                current_amount = current_amount - Decimal(resource['amount'])

            query = table.update().where(
                table.c.id == resource['account_id']).values(
                current_amount=current_amount.quantize(Decimal('.01')))
            await conn.execute(query)

        return resource

    async def after_remove(self, resource, request: web.Request, **kwargs):
        table = accounts.table

        async with Connection(request.app['engine']) as conn:
            query = select([table.c.current_amount, ]).where(
                table.c.id == resource['account_id'])
            current_amount = await conn.scalar(query)

            if resource['type'] == transactions.INCOME_TRANSACTION:
                current_amount = current_amount - Decimal(resource['amount'])
            elif resource['type'] == transactions.EXPENSE_TRANSACTION:
                current_amount = current_amount + Decimal(resource['amount'])

            query = table.update().where(
                table.c.id == resource['account_id']).values(
                current_amount=current_amount.quantize(Decimal('.01')))
            await conn.execute(query)
