from datetime import datetime

import sqlalchemy
from aiohttp import web
from decimal import Decimal
from sqlalchemy import and_, func, select

from ..exceptions import ValidationError
from ..storage import accounts, transactions
from ..utils.db import Connection
from . import base, auth


@auth.owner_required
@base.get_collection('accounts', serialize=accounts.serialize)
async def get_accounts(request: web.Request, **kwargs) -> tuple:
    owner = kwargs.get('owner')
    params = accounts.table.c.owner_id == owner.get('id')
    query = select([accounts.table]).where(params)
    total_query = select([func.count()]).select_from(
        accounts.table)

    return query, total_query


class AccountResourceHandler(base.ResourceHandler):
    decorators = (auth.owner_required, base.handle_response)

    resource_name = 'account'

    table = accounts.table
    schema = accounts.schema

    def serialize(self, resource):
        return accounts.serialize(resource)

    def get_resource_query(self, request: web.Request, **kwargs):
        owner = kwargs.get('owner')
        instance_id = base.get_instance_id(request, self.resource_key)
        return select([self.table]).where(and_(
            self.table.c.id == instance_id,
            self.table.c.owner_id == owner.get('id')
        ))

    async def validate(self, document, request, **kwargs):
        owner = kwargs.get('owner')
        instance = kwargs.get('instance', None)

        params = [
            self.table.c.name == document.get('name'),
            self.table.c.owner_id == owner.get('id')
        ]

        if instance is not None:
            params.append(self.table.c.id != instance.get('id'))

        query = select([func.count()]).select_from(self.table).where(
            and_(*params))

        async with Connection(request.app['engine']) as conn:
            count = await conn.scalar(query)
            if count > 0:
                raise ValidationError({'name': 'Already exists.'})

        if not instance:
            document.setdefault('owner_id', owner.get('id'))
            document.setdefault('created_on', datetime.now())
            document.setdefault('current_amount', document['original_amount'])

        return document

    async def after_update(self, resource, request, **kwargs):
        before = kwargs.get('before')

        if resource['original_amount'] == before['original_amount']:
            return resource

        original = Decimal(resource['original_amount'])
        table = transactions.table
        join = sqlalchemy.join(table, self.table,
                               self.table.c.id == table.c.account_id)
        async with Connection(request.app['engine']) as conn:
            expense_params = [
                self.table.c.id == resource.get('id'),
                table.c.type == transactions.EXPENSE_TRANSACTION
            ]
            query = select([func.sum(table.c.amount)]).select_from(
                table).select_from(join).where(and_(*expense_params))
            expenses = await conn.scalar(query)

            income_params = [
                self.table.c.id == resource.get('id'),
                table.c.type == transactions.INCOME_TRANSACTION
            ]
            query = select([func.sum(table.c.amount)]).select_from(
                table).select_from(join).where(and_(*income_params))
            incomes = await conn.scalar(query)
            if not incomes:
                incomes = 0

            current = original + incomes - expenses  # type: Decimal
            current_amount = current.quantize(Decimal('.01'))
            await conn.execute(self.table.update().where(
                self.table.c.id == resource.get('id')).values(
                current_amount=current_amount
            ))

        resource['current_amount'] = current_amount
        return resource
