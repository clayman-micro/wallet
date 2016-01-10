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

    def apply(self, amount: Decimal, transaction: Dict):
        if transaction['type'] == transactions.INCOME_TRANSACTION:
            amount = amount + Decimal(transaction['amount'])
        elif transaction['type'] == transactions.EXPENSE_TRANSACTION:
            amount = amount - Decimal(transaction['amount'])

        return amount

    def rollback(self, amount: Decimal, transaction: Dict):
        if transaction['type'] == transactions.INCOME_TRANSACTION:
            amount = amount - Decimal(transaction['amount'])
        elif transaction['type'] == transactions.EXPENSE_TRANSACTION:
            amount = amount + Decimal(transaction['amount'])

        return amount

    async def after_create(self, resource, request: web.Request, **kwargs):
        table = accounts.table

        async with Connection(request.app['engine']) as conn:
            current_amount = await conn.scalar(
                select([table.c.current_amount, ]).where(
                    table.c.id == resource['account_id'])
            )

            amount = self.apply(current_amount, resource)

            await conn.execute(table.update().where(
                table.c.id == resource['account_id']).values(
                    current_amount=amount.quantize(Decimal('.01'))))

    async def after_update(self, resource, request: web.Request, **kwargs):
        before = kwargs.get('before')
        table = accounts.table

        async with Connection(request.app['engine']) as conn:
            if resource['account_id'] != before['account_id']:
                current_amount = await conn.scalar(
                    select([table.c.current_amount, ]).where(
                        table.c.id == before['account_id']))

                amount = self.rollback(current_amount, before)

                await conn.execute(table.update().where(
                    table.c.id == before['account_id']).values(
                    current_amount=amount.quantize(Decimal('.01'))))

                current_amount = await conn.scalar(
                    select([table.c.current_amount, ]).where(
                        table.c.id == resource['account_id']))

                amount = self.apply(current_amount, resource)

                await conn.execute(table.update().where(
                    table.c.id == resource['account_id']).values(
                    current_amount=amount.quantize(Decimal('.01'))))
            else:
                current_amount = await conn.scalar(
                    select([table.c.current_amount, ]).where(
                        table.c.id == resource['account_id']))

                amount = self.rollback(current_amount, before)
                amount = self.apply(amount, resource)

                await conn.execute(table.update().where(
                    table.c.id == resource['account_id']).values(
                    current_amount=amount.quantize(Decimal('.01'))))

        return resource

    async def after_remove(self, resource, request: web.Request, **kwargs):
        table = accounts.table

        async with Connection(request.app['engine']) as conn:
            query = select([table.c.current_amount, ]).where(
                table.c.id == resource['account_id'])
            current_amount = await conn.scalar(query)

            amount = self.rollback(current_amount, resource)

            await conn.execute(table.update().where(
                table.c.id == resource['account_id']).values(
                current_amount=amount.quantize(Decimal('.01'))))
