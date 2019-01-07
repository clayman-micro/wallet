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


@user_required
async def remove(request: web.Request) -> web.Response:
    tag_key = get_instance_id(request, "tag_key")

    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        query = TagQuery(user=request["user"], key=tag_key)
        tags = await storage.tags.find(query=query)
        if not tags:
            raise web.HTTPNotFound()

        await storage.tags.remove(tags[0])

    return web.Response(status=204)
