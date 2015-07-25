import asyncio
from datetime import datetime
from aiohttp import web

from ..models import accounts, categories, transactions
from . import base


class TransactionAPIHandler(base.BaseAPIHandler):
    collection_name = 'transactions'
    resource_name = 'transaction'

    table = transactions.transactions_table
    schema = transactions.transactions_schema
    serializer = transactions.TransactionSerializer(exclude=('created_on', ))

    endpoints = (
        ('GET', '/transactions', 'get_transactions'),
        ('POST', '/transactions', 'create_transaction'),
        ('GET', '/transactions/{instance_id}', 'get_transaction'),
        ('PUT', '/transactions/{instance_id}', 'update_transaction'),
        ('DELETE', '/transactions/{instance_id}', 'remove_transaction'),
    )

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


class TransactionDetailAPIHandler(base.BaseAPIHandler):
    collection_name = 'details'
    resource_name = 'detail'

    table = transactions.transaction_details_table
    schema = transactions.transaction_details_schema
    serializer = transactions.TransactionDetailSerializer()

    endpoints = (
        ('GET', '/transactions/{transaction_id}/details', 'get_details'),
        ('POST', '/transactions/{transaction_id}/details', 'create_detail'),
        ('GET', '/transactions/{transaction_id}/details/{instance_id}',
         'get_detail'),
        ('PUT', '/transactions/{transaction_id}/details/{instance_id}',
         'update_detail'),
        ('DELETE', '/transactions/{transaction_id}/details/{instance_id}',
         'remove_detail'),
    )

    @asyncio.coroutine
    def validate_payload(self, request, payload, instance=None):
        transaction_id = request.match_info['transaction_id']

        with (yield from request.app.engine) as conn:
            query = transactions.transactions_table.select().where(
                transactions.transactions_table.c.id == transaction_id)
            transaction = yield from conn.scalar(query)

        if not transaction:
            return web.HTTPNotFound(text='Transaction not found')

        future = super(TransactionDetailAPIHandler, self).validate_payload(
            request, payload, instance)
        document, errors = yield from future

        document.setdefault('transaction_id', transaction_id)
        return document, None
