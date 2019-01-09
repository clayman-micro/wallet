from typing import Any, Dict

from aiohttp import web

from wallet.adapters.web import get_instance_id, get_payload, json_response
from wallet.adapters.web.users import user_required
from wallet.domain.entities import Tag
from wallet.services.tags import TagQuery, TagsService, TagValidator
from wallet.storage import DBStorage


def serialize_tag(instance: Tag) -> Dict[str, Any]:
    return {"id": instance.key, "name": instance.name}


@user_required
async def add(request: web.Request) -> web.Response:
    payload = await get_payload(request)

    validator = TagValidator()
    document = validator.validate_payload(payload)

    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        service = TagsService(storage)
        tag = await service.add(name=document["name"], user=request["user"])

    return json_response({"tag": serialize_tag(tag)}, status=201)


@user_required
async def fetch(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        query = TagQuery(user=request["user"])
        tags = await storage.tags.find(query=query)

    return json_response({"tags": list(map(serialize_tag, tags))})


async def get_tag(request: web.Request, storage: DBStorage, key: str) -> Tag:
    query = TagQuery(user=request["user"], key=get_instance_id(request, key))
    tags = await storage.tags.find(query=query)

    if not tags:
        raise web.HTTPNotFound()

    return tags[0]


@user_required
async def remove(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        tag = await get_tag(request, storage, "tag_key")
        await storage.tags.remove(tag)

    return web.Response(status=204)
