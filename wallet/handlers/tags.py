from datetime import datetime
from typing import Dict

from aiohttp import web

from wallet.handlers import (get_instance_id, get_payload, json_response,
                             register_handler)
from wallet.storage import AlreadyExist
from wallet.storage.tags import add_tag, fetch_tag, fetch_tags, remove_tag
from wallet.validation import ValidationError, Validator


schema = {
    'id': {'type': 'integer'},
    'name': {'type': 'string', 'required': True, 'empty': False}
}


async def get_tags(owner: Dict, request: web.Request) -> web.Response:
    name = None
    if 'name' in request.query and request.query['name']:
        name = request.query['name']

    async with request.app.db.acquire() as conn:
        tags = await fetch_tags(owner, conn=conn, name=name)

    meta = {'total': len(tags)}
    if name:
        meta['search'] = {'name': name}

    return json_response({'tags': tags, 'meta': meta})


async def create_tag(owner: Dict, request: web.Request) -> web.Response:
    payload = await get_payload(request)

    validator = Validator(schema)
    document = validator.validate_payload(payload)

    async with request.app.db.acquire() as conn:
        try:
            tag = await add_tag(owner, document['name'], datetime.now(), conn)
        except AlreadyExist:
            raise ValidationError({'name': 'Already exist'})

    return json_response({'tag': tag}, status=201)


async def get_tag(owner: Dict, request: web.Request) -> web.Response:
    tag_id = get_instance_id(request)

    async with request.app.db.acquire() as conn:
        tag = await fetch_tag(owner, tag_id, conn)

    return json_response({'tag': tag})


async def update_tag(owner: Dict, request: web.Request) -> web.Response:
    tag_id = get_instance_id(request)

    payload = await get_payload(request)

    async with request.app.db.acquire() as conn:
        tag = await fetch_tag(owner, tag_id, conn)

        validator = Validator(schema)
        document = validator.validate_payload(payload)

        query = '''
            SELECT COUNT(id) FROM tags
              WHERE name = $1 AND owner_id = $2 AND id != $3
        '''
        count = await conn.fetchval(query, payload['name'], owner['id'], tag_id)
        if count:
            raise ValidationError({'name': 'Already exist'})

        tag.update(**document)

    return json_response({'tag': tag})


async def delete_tag(owner: Dict, request: web.Request) -> web.Response:
    tag_id = get_instance_id(request)

    async with request.app.db.acquire() as conn:
        tag = await fetch_tag(owner, tag_id, conn)
        removed = await remove_tag(owner, tag, conn)

    return web.Response(status=200 if removed else 400)


def register(app: web.Application, url_prefix: str, name_prefix: str=None):
    with register_handler(app, url_prefix, name_prefix) as add:
        add('GET', '', get_tags, 'get_tags')
        add('POST', '', create_tag, 'create_tag')
        add('GET', '{instance_id}', get_tag, 'get_tag')
        add('PUT', '{instance_id}', update_tag, 'update_tag')
        add('DELETE', '{instance_id}', delete_tag, 'remove_tag')
