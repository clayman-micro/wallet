import asyncio

from aiohttp import web
from sqlalchemy import and_

from ..models import categories
from . import base, auth


class CategoryAPIHandler(base.BaseAPIHandler):
    collection_name = 'categories'
    resource_name = 'category'

    table = categories.categories_table
    schema = categories.categories_schema
    serializer = categories.CategorySerializer()

    decorators = (
        base.allow_cors(methods=('GET', 'POST', 'PUT', 'DELETE')),
        auth.owner_required,
    )

    endpoints = (
        ('GET', '/categories', 'get_categories'),
        ('POST', '/categories', 'create_category'),
        ('GET', '/categories/{instance_id}', 'get_category'),
        ('PUT', '/categories/{instance_id}', 'update_category'),
        ('DELETE', '/categories/{instance_id}', 'remove_category'),

        ('OPTIONS', '/categories', 'categories_cors'),
        ('OPTIONS', '/categories/{instance_id}', 'category_cors')
    )

    @asyncio.coroutine
    def options(self, request):
        print(request.headers)
        return web.Response(status=200)

    @asyncio.coroutine
    def validate_payload(self, request, payload, instance=None):
        if instance:
            del instance['owner_id']

        future = super(CategoryAPIHandler, self).validate_payload(
            request, payload, instance)
        document, errors = yield from future

        if errors:
            return None, errors

        document.setdefault('owner_id', request.owner.get('id'))

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
            self.table.c.owner_id == request.owner.get('id')
        )

    def get_instance_query(self, request, instance_id):
        return self.table.select().where(
            and_(self.table.c.id == instance_id,
                 self.table.c.owner_id == request.owner.get('id'))
        )
