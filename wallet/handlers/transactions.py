import asyncio
from datetime import datetime
from decimal import Decimal
from functools import wraps
from aiohttp import web

from ..models import accounts, categories, transactions
from . import base, auth
import sqlalchemy
from sqlalchemy import select


class TransactionAPIHandler(base.BaseAPIHandler):
    collection_name = 'transactions'
    resource_name = 'transaction'

    table = transactions.transactions_table
    schema = transactions.transactions_schema
    serializer = transactions.TransactionSerializer()

    decorators = (
        base.allow_cors(methods=('GET', 'POST', 'PUT', 'DELETE')),
        auth.owner_required,
    )

    endpoints = (
        ('GET', '/transactions', 'get_transactions'),
        ('POST', '/transactions', 'create_transaction'),
        ('GET', '/transactions/{instance_id}', 'get_transaction'),
        ('PUT', '/transactions/{instance_id}', 'update_transaction'),
        ('DELETE', '/transactions/{instance_id}', 'remove_transaction'),

        ('OPTIONS', '/transactions', 'transactions_cors'),
        ('OPTIONS', '/transactions/{instance_id}', 'transaction_cors')
    )

    async def options(self, request):
        return web.Response(status=200)

    @asyncio.coroutine
    def validate_payload(self, request, payload, instance=None):
        future = super(TransactionAPIHandler, self).validate_payload(
            request, payload, instance)
        document, errors = yield from future

        if errors:
            return None, errors

        document.setdefault('created_on', datetime.now())

        errors = {}
        with (yield from request.app.engine) as conn:
            if instance or 'account_id' in payload.keys():
                query = accounts.accounts_table.select().where(
                    accounts.accounts_table.c.id == document.get('account_id'))
                account = yield from conn.scalar(query)

                if not account:
                    errors.update(account_id='Account does not exists.')

            if instance or 'categories_id' in payload.keys():
                table = categories.categories_table
                query = table.select().where(
                    table.c.id == document.get('category_id'))
                category = yield from conn.scalar(query)

                if not category:
                    errors.update(category_id='Category does not exists.')

        return document, errors

    @asyncio.coroutine
    def after_create_instance(self, request, instance):
        table = accounts.accounts_table

        with (yield from request.app.engine) as conn:
            query = select([table.c.current_amount, ]).where(
                table.c.id == instance['account_id']
            )
            current_amount = yield from conn.scalar(query)

            if instance['type'] == transactions.INCOME_TRANSACTION:
                current_amount = current_amount + Decimal(instance['amount'])
            elif instance['type'] == transactions.EXPENSE_TRANSACTION:
                current_amount = current_amount - Decimal(instance['amount'])

            query = table.update().where(
                table.c.id == instance['account_id']).values(
                current_amount=current_amount.quantize(Decimal('.01')))
            yield from conn.execute(query)

    @asyncio.coroutine
    def after_update_instance(self, request, instance, before):
        table = accounts.accounts_table

        with (yield from request.app.engine) as conn:
            query = select([table.c.current_amount, ]).where(
                table.c.id == instance['account_id'])
            current_amount = yield from conn.scalar(query)

            if before['type'] == transactions.INCOME_TRANSACTION:
                current_amount = current_amount - before['amount']
            elif before['type'] == transactions.EXPENSE_TRANSACTION:
                current_amount = current_amount + before['amount']

            if instance['type'] == transactions.INCOME_TRANSACTION:
                current_amount = current_amount + Decimal(instance['amount'])
            elif instance['type'] == transactions.EXPENSE_TRANSACTION:
                current_amount = current_amount - Decimal(instance['amount'])

            query = table.update().where(
                table.c.id == instance['account_id']).values(
                current_amount=current_amount.quantize(Decimal('.01')))
            yield from conn.execute(query)

    @asyncio.coroutine
    def after_remove_instance(self, request, instance):
        table = accounts.accounts_table

        with (yield from request.app.engine) as conn:
            query = select([table.c.current_amount, ]).where(
                table.c.id == instance['account_id'])
            current_amount = yield from conn.scalar(query)

            if instance['type'] == transactions.INCOME_TRANSACTION:
                current_amount = current_amount - Decimal(instance['amount'])
            elif instance['type'] == transactions.EXPENSE_TRANSACTION:
                current_amount = current_amount + Decimal(instance['amount'])

            query = table.update().where(
                table.c.id == instance['account_id']).values(
                current_amount=current_amount.quantize(Decimal('.01')))
            yield from conn.execute(query)

    def get_collection_query(self, request):
        accounts_alias = accounts.accounts_table.alias()
        join = sqlalchemy.join(self.table, accounts_alias,
                               accounts_alias.c.id == self.table.c.account_id)
        return self.table.select().select_from(join).where(
            accounts_alias.c.owner_id == request.owner.get('id'))

    def get_instance_query(self, request, instance_id):
        accounts_alias = accounts.accounts_table.alias()
        join = sqlalchemy.join(self.table, accounts_alias,
                               accounts_alias.c.id == self.table.c.account_id)
        return self.table.select().select_from(join).where(
            sqlalchemy.and_(
                accounts_alias.c.owner_id == request.owner.get('id'),
                self.table.c.id == instance_id
            )
        )


def transaction_required(f):
    @asyncio.coroutine
    @wraps(f)
    def wrapper(*args, **kwargs):
        """ Check that transaction exists and it's owner match request.owner

        method is a coroutine
        """
        if asyncio.iscoroutinefunction(f):
            coro = f
        else:
            coro = asyncio.coroutine(f)
        request = args[-1]

        transaction_id = request.match_info['transaction_id']

        with (yield from request.app.engine) as conn:
            query = sqlalchemy.select([
                transactions.transactions_table.c.id,
                accounts.accounts_table.c.owner_id
            ], from_obj=sqlalchemy.join(
                transactions.transactions_table,
                accounts.accounts_table)
            ).where(
                transactions.transactions_table.c.id == transaction_id
            )
            result = yield from conn.execute(query)
            row = yield from result.fetchone()

            if not row:
                return web.HTTPNotFound(text='Transaction not found')

            if row.owner_id != request.owner.get('id'):
                return web.HTTPForbidden(text='You don\'t own this transaction')

        result = yield from coro(*args, **kwargs)
        return result
    return wrapper


class TransactionDetailAPIHandler(base.BaseAPIHandler):
    collection_name = 'details'
    resource_name = 'detail'

    table = transactions.transaction_details_table
    schema = transactions.transaction_details_schema
    serializer = transactions.TransactionDetailSerializer()

    decorators = (
        base.allow_cors(methods=('GET', 'POST', 'PUT', 'DELETE')),
        transaction_required,
        auth.owner_required
    )

    endpoints = (
        ('GET', '/transactions/{transaction_id}/details', 'get_details'),
        ('POST', '/transactions/{transaction_id}/details', 'create_detail'),
        ('GET', '/transactions/{transaction_id}/details/{instance_id}',
         'get_detail'),
        ('PUT', '/transactions/{transaction_id}/details/{instance_id}',
         'update_detail'),
        ('DELETE', '/transactions/{transaction_id}/details/{instance_id}',
         'remove_detail'),

        ('OPTIONS', '/transactions/{transaction_id}/details',
            'transaction_details_cors'),
        ('OPTIONS', '/transactions/{transaction_id}/details/{instance_id}',
            'transaction_detail_cors')
    )

    def get_collection_query(self, request):
        transaction_id = request.match_info['transaction_id']

        join = sqlalchemy.join(self.table, transactions.transactions_table)
        return self.table.select(from_obj=join).where(
            transactions.transactions_table.c.id == transaction_id)

    def get_instance_query(self, request, instance_id):
        transaction_id = request.match_info['transaction_id']

        join = sqlalchemy.join(self.table, transactions.transactions_table)
        return self.table.select(from_obj=join).where(
            sqlalchemy.and_(
                transactions.transactions_table.c.id == transaction_id,
                self.table.c.id == instance_id
            )
        )

    @asyncio.coroutine
    def validate_payload(self, request, payload, instance=None):
        if not instance:
            payload.setdefault('transaction_id',
                               request.match_info['transaction_id'])

        future = super(TransactionDetailAPIHandler, self).validate_payload(
            request, payload, instance)
        document, errors = yield from future

        return document, errors
