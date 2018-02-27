from aiohttp import web

from wallet.adapters.operations import OperationsAPIAdapter, OperationTagsAPIAdapter
from wallet.entities import EntityAlreadyExist, Owner, Tag
from wallet.handlers import get_instance_id, get_payload, json_response
from wallet.repositories.accounts import AccountsRepository
from wallet.repositories.operations import OperationsRepo
from wallet.repositories.tags import TagsRepository
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


async def fetch_tags(owner: Owner, request: web.Request) -> web.Response:
    account_pk = get_instance_id(request, key='account')
    operation_pk = get_instance_id(request, key='operation')

    async with request.app.db.acquire() as conn:
        accounts_repo = AccountsRepository(conn=conn)
        operations_repo = OperationsRepo(conn=conn)
        tags_repo = TagsRepository(conn=conn)

        adapter = OperationTagsAPIAdapter(
            accounts_repo, operations_repo, tags_repo
        )
        response = await adapter.fetch_tags(owner, account_pk, operation_pk)

    return json_response(response)


async def add_tag(owner: Owner, request: web.Request) -> web.Response:
    payload = await get_payload(request)

    account_pk = get_instance_id(request, key='account')
    operation_pk = get_instance_id(request, key='operation')

    async with request.app.db.acquire() as conn:
        accounts_repo = AccountsRepository(conn=conn)
        operations_repo = OperationsRepo(conn=conn)
        tags_repo = TagsRepository(conn=conn)

        adapter = OperationTagsAPIAdapter(
            accounts_repo, operations_repo, tags_repo
        )
        response = await adapter.add_tag(owner, account_pk, operation_pk,
                                         payload)

    return json_response(response, 201)


async def remove_tag(owner: Owner, request: web.Request) -> web.Response:
    account_pk = get_instance_id(request, key='account')
    operation_pk = get_instance_id(request, key='operation')
    tag_pk = get_instance_id(request, key='tag')

    async with request.app.db.acquire() as conn:
        accounts_repo = AccountsRepository(conn=conn)
        operations_repo = OperationsRepo(conn=conn)
        tags_repo = TagsRepository(conn=conn)

        adapter = OperationTagsAPIAdapter(
            accounts_repo, operations_repo, tags_repo
        )
        await adapter.remove_tag(owner, account_pk, operation_pk, tag_pk)

    return web.Response()
