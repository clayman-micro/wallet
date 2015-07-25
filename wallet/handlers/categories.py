import asyncio

from sqlalchemy import and_

from ..models import categories
from . import base


class CategoryAPIHandler(base.BaseAPIHandler):
    collection_name = 'categories'
    resource_name = 'category'

    table = categories.categories_table
    schema = categories.categories_schema
    serializer = categories.CategorySerializer()

    endpoints = (
        ('GET', '/categories', 'get_categories'),
        ('POST', '/categories', 'create_category'),
        ('GET', '/categories/{instance_id}', 'get_category'),
        ('PUT', '/categories/{instance_id}', 'update_category'),
        ('DELETE', '/categories/{instance_id}', 'remove_category')
    )

    @asyncio.coroutine
    def validate_payload(self, request, payload, instance=None):
        future = super(CategoryAPIHandler, self).validate_payload(
            request, payload, instance)
        document, errors = yield from future

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
