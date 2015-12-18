from datetime import datetime

from aiohttp import web
from sqlalchemy import and_, func, select

from ..exceptions import ValidationError
from ..storage import accounts
from ..utils import Connection
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
        # TODO: update current amount when update original amount
        pass
