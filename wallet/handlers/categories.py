import asyncio

from cerberus import Validator
from sqlalchemy import and_

from ..models.categories import (categories_table, categories_schema,
                                 CategorySerializer)
from . import base


serializer = CategorySerializer()

get_categories = base.get_collection(categories_table, serializer, 'categories')
get_category = base.get_resource(categories_table, serializer, 'category')
remove_category = base.delete_resource(categories_table, 'category')


@base.create_resource(categories_table, serializer, 'category')
@asyncio.coroutine
def create_category(request, payload):
    validator = Validator(schema=categories_schema)
    if not validator.validate(payload):
        return None, validator.errors

    document = validator.document

    with (yield from request.app.engine) as conn:
        query = categories_table.select().where(
            categories_table.c.name == payload.get('name'))
        result = yield from conn.scalar(query)

    if result:
        return None, {'name': 'Already exists.'}
    else:
        return document, None


@base.update_resource(categories_table, serializer, 'category')
@asyncio.coroutine
def update_category(request, payload, instance):
    validator = Validator(schema=categories_schema)
    if not validator.validate(instance):
        return None, validator.errors

    document = validator.document

    with (yield from request.app.engine) as conn:
        query = categories_table.select().where(and_(
            categories_table.c.name == document.get('name'),
            categories_table.c.id != document.get('id')
        ))
        result = yield from conn.scalar(query)

    if result:
        return None, {'name': 'Already exists.'}
    else:
        return document, None
