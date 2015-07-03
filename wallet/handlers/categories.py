import asyncio
from datetime import datetime

from aiohttp import web
from cerberus import Validator

from ..models.categories import categories_table, categories_schema
from .base import get_payload, json_response, reverse_url


@asyncio.coroutine
def get_categories(request):
    with (yield from request.app.engine) as conn:
        query = categories_table.select().limit(10)
        result = yield from conn.execute(query)

        response = {
            'categories': [],
            'meta': {
                'total': 0,
                'limit': 10,
                'collection_url': reverse_url(request, 'api.get_categories')
            }
        }

        if result.returns_rows:
            total = 0
            for item in (yield from result.fetchall()):
                category = {
                    'id': item.id,
                    'name': item.name,
                    'type': item.type,
                }
                response['categories'].append(category)
                total += 1

            response['meta']['total'] = total
    return json_response(response)


@asyncio.coroutine
def get_category(request):
    instance_id = request.match_info['instance_id']

    with (yield from request.app.engine) as conn:
        query = categories_table.select().where(
            categories_table.c.id == instance_id)
        result = yield from conn.execute(query)

        category = yield from result.fetchone()

        if category:
            return json_response({
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'type': category.type
                },
                'meta': {
                    'collection_url': reverse_url(request, 'api.get_categories'),
                    'resource_url': reverse_url(request, 'api.get_category',
                                                {'instance_id': category.id})
                }
            })
        else:
            raise web.HTTPNotFound(text='Category not found')


@asyncio.coroutine
def create_category(request):
    payload = yield from get_payload(request)

    validator = Validator(schema=categories_schema)
    if not validator.validate(payload):
        return json_response({
            'errors': validator.errors
        }, status=400)

    with (yield from request.app.engine) as conn:
        query = categories_table.select().where(
            categories_table.c.name == payload.get('name'))
        res = yield from conn.scalar(query)

        if res:
            return json_response({
                'errors': {
                    'name': 'Already exists.'
                }
            }, status=400)

        query = categories_table.insert().values(name=payload.get('name'),
                                                 type=payload.get('type'))
        uid = yield from conn.scalar(query)

    return json_response({
        'category': {
            'id': uid,
            'name': payload.get('name'),
            'type': payload.get('type')
        }
    }, status=201)


@asyncio.coroutine
def update_category(request):
    instance_id = request.match_info['instance_id']

    with (yield from request.app.engine) as conn:
        query = categories_table.select().where(
            categories_table.c.id == instance_id)
        result = yield from conn.execute(query)

        row = yield from result.fetchone()
        category = dict(zip(row.keys(), row.values()))

    if not category:
        raise web.HTTPNotFound(text='Category not found')

    payload = yield from get_payload(request)

    category.update(**payload)

    validator = Validator(schema=categories_schema)
    if not validator.validate(category):
        return json_response({
            'errors': validator.errors
        }, status=400)

    with (yield from request.app.engine) as conn:
        query = categories_table.update().where(
            categories_table.c.id == category.get('id')).values(**payload)
        result = yield from conn.execute(query)

        if result.rowcount:
            return json_response({
                'category': {
                    'id': category.get('id'),
                    'name': category.get('name'),
                    'type': category.get('type')
                }
            })
        else:
            raise web.HTTPNotFound(text='Category not found')


@asyncio.coroutine
def remove_category(request):
    instance_id = request.match_info['instance_id']

    with (yield from request.app.engine) as conn:
        query = categories_table.delete().where(
            categories_table.c.id == instance_id)
        result = yield from conn.execute(query)

        if result.rowcount:
            return web.Response(text='removed')
        else:
            raise web.HTTPNotFound(text='Category not found')
