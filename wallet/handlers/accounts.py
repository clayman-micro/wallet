import asyncio
from datetime import datetime

from sqlalchemy import and_

from ..models import accounts
from . import base, auth


class AccountAPIHandler(base.BaseAPIHandler):
    collection_name = 'accounts'
    resource_name = 'account'

    table = accounts.accounts_table
    schema = accounts.accounts_schema
    serializer = accounts.AccountSerializer(exclude=('created_on', ))

    decorators = (auth.owner_required, )

    endpoints = (
        ('GET', '/accounts', 'get_accounts'),
        ('POST', '/accounts', 'create_account'),
        ('GET', '/accounts/{instance_id}', 'get_account'),
        ('PUT', '/accounts/{instance_id}', 'update_account'),
        ('DELETE', '/accounts/{instance_id}', 'remove_account')
    )

    @asyncio.coroutine
    def validate_payload(self, request, payload, instance=None):
        if instance:
            del instance['owner_id']

        future = super(AccountAPIHandler, self).validate_payload(
            request, payload, instance)
        document, errors = yield from future

        if errors:
            return None, errors

        document.setdefault('owner_id', request.owner.get('id'))
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

    def get_collection_query(self, request):
        return self.table.select().where(
            self.table.c.owner_id == request.owner.get('id'))

    def get_instance_query(self, request, instance_id):
        return self.table.select().where(
            and_(self.table.c.id == instance_id,
                 self.table.c.owner_id == request.owner.get('id'))
        )
