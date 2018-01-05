from aiohttp import web

from wallet.adapters.operations import OperationsAPIAdapter
from wallet.entities import Owner
from wallet.handlers import get_instance_id, get_payload, json_response
from wallet.repositories.accounts import AccountsRepository
from wallet.repositories.operations import OperationsRepo
from wallet.utils.operations import OpsFilter


async def get_operations(owner: Owner, request: web.Request) -> web.Response:
    filters = OpsFilter.from_dict({
        'year': request.query.get('year', None),
        'month': request.query.get('month', None),
    })

    async with request.app.db.acquire() as conn:
        accounts_repo = AccountsRepository(conn=conn)
        operations_repo = OperationsRepo(conn=conn)

        adapter = OperationsAPIAdapter(accounts_repo, operations_repo)
        response = await adapter.fetch(
            owner, get_instance_id(request, key='account'), filters=filters
        )

    return json_response(response, 200)


async def add_operation(owner: Owner, request: web.Request) -> web.Response:
    async with request.app.db.acquire() as conn:
        accounts_repo = AccountsRepository(conn=conn)
        operations_repo = OperationsRepo(conn=conn)

        adapter = OperationsAPIAdapter(accounts_repo, operations_repo)

        payload = await get_payload(request)
        response = await adapter.add_operation(
            owner, get_instance_id(request, key='account'), payload
        )

    return json_response(response, 201)


async def get_operation(owner: Owner, request: web.Request) -> web.Response:
    async with request.app.db.acquire() as conn:
        accounts_repo = AccountsRepository(conn=conn)
        operations_repo = OperationsRepo(conn=conn)

        adapter = OperationsAPIAdapter(accounts_repo, operations_repo)
        response = await adapter.fetch_operation(
            owner, get_instance_id(request, key='account'),
            get_instance_id(request, key='operation')
        )

    return json_response(response, 200)


async def update_operation(owner: Owner, request: web.Request) -> web.Response:
    async with request.app.db.acquire() as conn:
        accounts_repo = AccountsRepository(conn=conn)
        operations_repo = OperationsRepo(conn=conn)

        adapter = OperationsAPIAdapter(accounts_repo, operations_repo)

        payload = await get_payload(request)
        response = await adapter.update_operation(
            owner, get_instance_id(request, key='account'),
            get_instance_id(request, key='operation'), payload
        )

    return json_response(response, 200)


async def remove_operation(owner: Owner, request: web.Request) -> web.Response:
    async with request.app.db.acquire() as conn:
        accounts_repo = AccountsRepository(conn=conn)
        operations_repo = OperationsRepo(conn=conn)

        adapter = OperationsAPIAdapter(accounts_repo, operations_repo)
        response = await adapter.remove_operation(
            owner, get_instance_id(request, key='account'),
            get_instance_id(request, key='operation')
        )

    return json_response(response, 200)
