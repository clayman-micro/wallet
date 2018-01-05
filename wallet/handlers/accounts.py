from aiohttp import web

from wallet.adapters.accounts import AccountsAPIAdapter
from wallet.entities import Owner
from wallet.handlers import get_instance_id, get_payload, json_response
from wallet.repositories.accounts import AccountsRepository
from wallet.repositories.operations import OperationsRepo
from wallet.utils.accounts import AccountsFilter


async def get_accounts(owner: Owner, request: web.Request) -> web.Response:
    filters = AccountsFilter(name=request.query.get('name', None))

    async with request.app.db.acquire() as conn:
        repo = AccountsRepository(conn)

        adapter = AccountsAPIAdapter(repo)
        response = await adapter.fetch(owner, filters)

    return json_response(response)


async def add_account(owner: Owner, request: web.Request) -> web.Response:
    payload = await get_payload(request)

    async with request.app.db.acquire() as conn:
        repo = AccountsRepository(conn)

        adapter = AccountsAPIAdapter(repo)
        response = await adapter.add_account(owner, payload)

    return json_response(response, status=201)


async def get_account(owner: Owner, request: web.Request) -> web.Response:
    async with request.app.db.acquire() as conn:
        repo = AccountsRepository(conn)

        adapter = AccountsAPIAdapter(repo)
        response = await adapter.fetch_account(owner, get_instance_id(request))

    return json_response(response)


async def update_account(owner: Owner, request: web.Request) -> web.Response:
    instance_id = get_instance_id(request)
    payload = await get_payload(request)

    async with request.app.db.acquire() as conn:
        repo = AccountsRepository(conn)
        operations_repo = OperationsRepo(conn)

        adapter = AccountsAPIAdapter(repo, operations_repo)
        response = await adapter.update_account(
            owner, pk=instance_id, payload=payload
        )

    return json_response(response)


async def remove_account(owner: Owner, request: web.Request) -> web.Response:
    instance_id = get_instance_id(request)

    async with request.app.db.acquire() as conn:
        repo = AccountsRepository(conn)

        adapter = AccountsAPIAdapter(repo)
        await adapter.remove_account(owner, pk=instance_id)

    return web.Response(status=200)
