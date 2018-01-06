from aiohttp import web

from wallet.adapters.tags import TagsAPIAdapter
from wallet.entities import Owner
from wallet.handlers import get_instance_id, get_payload, json_response
from wallet.repositories.tags import TagsRepository
from wallet.utils.tags import TagsFilter


async def get_tags(owner: Owner, request: web.Request) -> web.Response:
    filters = TagsFilter(name=request.query.get('name', None))

    async with request.app.db.acquire() as conn:
        repo = TagsRepository(conn)

        adapter = TagsAPIAdapter(repo)
        response = await adapter.fetch(owner, filters)

    return json_response(response)


async def add_tag(owner: Owner, request: web.Request) -> web.Response:
    payload = await get_payload(request)

    async with request.app.db.acquire() as conn:
        repo = TagsRepository(conn)

        adapter = TagsAPIAdapter(repo)
        response = await adapter.add_tag(owner, payload)

    return json_response(response, status=201)


async def get_tag(owner: Owner, request: web.Request) -> web.Response:
    tag_pk = get_instance_id(request, 'tag')

    async with request.app.db.acquire() as conn:
        repo = TagsRepository(conn)

        adapter = TagsAPIAdapter(repo)
        response = await adapter.fetch_tag(owner, tag_pk)

    return json_response(response)


async def update_tag(owner: Owner, request: web.Request) -> web.Response:
    tag_pk = get_instance_id(request, 'tag')
    payload = await get_payload(request)

    async with request.app.db.acquire() as conn:
        repo = TagsRepository(conn)

        adapter = TagsAPIAdapter(repo)
        response = await adapter.update_tag(owner, tag_pk, payload)

    return json_response(response)


async def remove_tag(owner: Owner, request: web.Request) -> web.Response:
    async with request.app.db.acquire() as conn:
        repo = TagsRepository(conn)

        adapter = TagsAPIAdapter(repo)
        await adapter.remove_tag(owner, get_instance_id(request, 'tag'))

    return web.Response()
