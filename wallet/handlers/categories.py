from typing import Dict

from aiohttp import web
from sqlalchemy import and_, func, select

from ..exceptions import ValidationError
from ..storage import categories
from ..utils.db import Connection
from . import base, auth


@auth.owner_required
@base.get_collection('categories')
async def get_categories(request: web.Request, **kwargs) -> tuple:
    owner = kwargs.get('owner')
    params = (categories.table.c.owner_id == owner.get('id'), )
    query = select([categories.table]).where(*params)
    total_query = select([func.count()]).select_from(
        categories.table).where(*params)

    return query, total_query


class CategoryResourceHandler(base.ResourceHandler):
    decorators = (auth.owner_required, base.handle_response)

    resource_name = 'category'

    table = categories.table
    schema = categories.schema

    def get_resource_query(self, request: web.Request, **kwargs):
        owner = kwargs.get('owner')
        instance_id = base.get_instance_id(request)
        return select([self.table]).where(and_(
            self.table.c.id == instance_id,
            self.table.c.owner_id == owner.get('id')
        ))

    async def validate(self, document: Dict, request: web.Request, **kwargs):
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
                raise ValidationError({'name': 'Already exists'})

        if not instance:
            document.setdefault('owner_id', owner.get('id'))

        return document
