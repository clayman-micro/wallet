from functools import partial
from typing import Dict

import sqlalchemy
from aiohttp import web

from wallet.utils.handlers import register_handler
from ..exceptions import ValidationError
from ..storage import categories
from ..storage.base import serialize
from . import base, auth


schema = {
    'id': {
        'type': 'integer'
    },
    'name': {
        'type': 'string',
        'maxlength': 255,
        'required': True,
        'empty': False
    },
    'owner_id': {
        'type': 'integer',
        'coerce': int,
        'readonly': True
    }
}


async def validate(document, request, owner, resource=None):
    params = [
        categories.table.c.name == document.get('name'),
        categories.table.c.owner_id == owner.get('id')
    ]

    if resource is not None:
        params.append(categories.table.c.id != resource.get('id'))

    async with request.app['engine'].acquire() as conn:
        count = await conn.scalar(
            sqlalchemy.select([sqlalchemy.func.count()])
                .select_from(categories.table)
                .where(sqlalchemy.and_(*params))
        )
        if count > 0:
            raise ValidationError({'name': 'Already exists'})

    if not resource:
        document.setdefault('owner_id', owner.get('id'))

    return document


serialize = partial(serialize, exclude=('owner_id', ))


@auth.owner_required
@base.handle_response
async def get_categories(request: web.Request, owner: Dict) -> Dict:
    collection = []

    params = categories.table.c.owner_id == owner.get('id')
    async with request.app['engine'].acquire() as conn:
        query = sqlalchemy.select([categories.table]).where(params)
        async for row in conn.execute(query):
            category = dict(zip(row.keys(), row.values()))
            collection.append(category)

        total = await conn.scalar(
            sqlalchemy.select([sqlalchemy.func.count()])
                .select_from(categories.table)
                .where(params)
        )

    return {
        'categories': list(map(serialize, collection)),
        'meta': {
            'count': len(collection),
            'total': total
        }
    }


@auth.owner_required
@base.handle_response
async def create_category(request: web.Request, owner: Dict) -> Dict:
    category = await base.create_resource(request, categories.table, schema,
                                          validate, owner=owner)
    return base.json_response({'category': serialize(category)}, status=201)


@auth.owner_required
@base.handle_response
async def get_category(request: web.Request, owner: Dict) -> Dict:
    instance_id = base.get_instance_id(request)
    category = await categories.get_category(instance_id, owner,
                                             request.app['engine'])
    return {'category': serialize(category)}


@auth.owner_required
@base.handle_response
async def update_category(request: web.Request, owner: Dict) -> Dict:
    instance_id = base.get_instance_id(request)

    # Get resource
    engine = request.app['engine']
    category = await categories.get_category(instance_id, owner, engine)

    # Validate payload
    payload = await base.get_payload(request)
    document = base.validate_payload(payload, schema, update=True)

    # Validate resource after update
    before = category.copy()
    category.update(document)
    resource = await validate(category, request, owner, resource=category)

    # Update resource
    after = await base.update_instance(resource, categories.table, engine)

    return {'category': serialize(after)}


@auth.owner_required
@base.handle_response
async def remove_category(request: web.Request, owner: Dict) -> Dict:
    instance_id = base.get_instance_id(request)
    engine = request.app['engine']

    category = await categories.get_category(instance_id, owner, engine=engine)
    await base.remove_instance(category, categories.table, engine=engine)
    return {'category': 'removed'}


def register(app, url_prefix, name_prefix):
    with register_handler(app, url_prefix, name_prefix) as register:
        register('GET', '', get_categories, 'get_categories')
        register('POST', '', create_category, 'create_category')
        register('GET', '{instance_id}', get_category, 'get_category')
        register('PUT', '{instance_id}', update_category, 'update_category')
        register('DELETE', '{instance_id}', remove_category, 'remove_category')
