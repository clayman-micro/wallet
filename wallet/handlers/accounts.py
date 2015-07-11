import asyncio
from datetime import datetime

from cerberus import Validator
from sqlalchemy import and_

from ..models.accounts import accounts_table, accounts_schema, AccountSerializer
from . import base


serializer = AccountSerializer(exclude=('created_on', ))

get_accounts = base.get_collection(accounts_table, serializer, 'accounts')
get_account = base.get_resource(accounts_table, serializer, 'account')
remove_account = base.delete_resource(accounts_table, 'account')


@base.create_resource(accounts_table, serializer, 'account')
@asyncio.coroutine
def create_account(request, payload):
    validator = Validator(schema=accounts_schema)
    if not validator.validate(payload):
        return None, validator.errors

    document = validator.document
    document.setdefault('created_on', datetime.now())
    document.setdefault('current_amount', 0)

    with (yield from request.app.engine) as conn:
        query = accounts_table.select().where(
            accounts_table.c.name == document.get('name'))
        result = yield from conn.scalar(query)

    if result:
        return None, {'name': 'Already exists.'}
    else:
        return document, None


@base.update_resource(accounts_table, serializer, 'account')
@asyncio.coroutine
def update_account(request, payload, instance):
    validator = Validator(schema=accounts_schema)
    if not validator.validate(instance):
        return None, validator.errors

    document = validator.document

    with (yield from request.app.engine) as conn:
        query = accounts_table.select().where(and_(
            accounts_table.c.name == document.get('name'),
            accounts_table.c.id != document.get('id')
        ))
        result = yield from conn.scalar(query)

    if result:
        return None, {'name': 'Already exists.'}
    else:
        return document, None
