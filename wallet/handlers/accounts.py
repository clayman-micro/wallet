import asyncio
from datetime import datetime

from sqlalchemy import and_

from ..models import accounts
from . import base


class AccountAPIHandler(base.BaseAPIHandler):
    collection_name = 'accounts'
    resource_name = 'account'

    table = accounts.accounts_table
    schema = accounts.accounts_schema
    serializer = accounts.AccountSerializer(exclude=('created_on', ))

    endpoints = (
        ('GET', '/accounts', 'get_accounts'),
        ('POST', '/accounts', 'create_account'),
        ('GET', '/accounts/{instance_id}', 'get_account'),
        ('PUT', '/accounts/{instance_id}', 'update_account'),
        ('DELETE', '/accounts/{instance_id}', 'remove_account')
    )

    @asyncio.coroutine
    def validate_payload(self, request, payload, instance=None):
        future = super(AccountAPIHandler, self).validate_payload(
            request, payload, instance)
        document, errors = yield from future

        if errors:
            return None, errors

        document.setdefault('created_on', datetime.now())
        document.setdefault('current_amount', 0)

        params = self.table.c.name == document.get('name')
        if instance:
            params = and_(params, self.table.c.id != document.get('id'))

        with (yield from request.app.engine) as conn:
            query = self.table.select().where(params)
            result = yield from conn.scalar(query)

        if result:
            return None, {'name': 'Already exists.'}
        else:
            return document, None
