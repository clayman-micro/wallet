from typing import Any, Dict

from aiohttp import web

from wallet.adapters.web import get_instance_id, get_payload, json_response
from wallet.adapters.web.users import user_required
from wallet.domain.entities import Operation
from wallet.domain.storage import AccountQuery, OperationQuery
from wallet.services.operations import OperationsService, OperationValidator
from wallet.storage import DBStorage


def serialize_operation(instance: Operation) -> Dict[str, Any]:
    result = {
        "id": instance.key,
        "amount": round(instance.amount),
        "type": instance.type.value,
        "description": instance.description,
        "account": {"id": instance.account.key},
        "created_on": instance.created_on.isoformat(),
    }

    if instance.tags:
        result["tags"] = [{"id": tag.key, "name": tag.name} for tag in instance.tags]

    return result


@user_required
async def add(request: web.Request) -> web.Response:
    account_key = get_instance_id(request, "account_key")

    payload = await get_payload(request)

    validator = OperationValidator()
    document = validator.validate_payload(payload)

    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        query = AccountQuery(user=request["user"], key=account_key)
        accounts = await storage.accounts.find(query=query)

        if not accounts:
            raise web.HTTPNotFound()

        service = OperationsService(storage)
        operation = await service.add_to_account(
            account=accounts[0],
            amount=document["amount"],
            description=document.get("description", ""),
            operation_type=document["type"],
            created_on=document["created_on"],
        )

    response = {"operation": serialize_operation(operation)}

    return json_response(response, status=201)


@user_required
async def search(request: web.Request) -> web.Response:
    account_key = get_instance_id(request, "account_key")

    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        query = AccountQuery(user=request["user"], key=account_key)
        accounts = await storage.accounts.find(query=query)

        if not accounts:
            raise web.HTTPNotFound()

        ops_query = OperationQuery(account=accounts[0])
        operations = await storage.operations.find(query=ops_query)

    response = {
        "operations": [serialize_operation(operation) for operation in operations]
    }

    return json_response(response)


@user_required
async def fetch(request: web.Request) -> web.Response:
    account_key = get_instance_id(request, "account_key")
    operation_key = get_instance_id(request, "operation_key")

    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        accounts = await storage.accounts.find(
            query=AccountQuery(user=request["user"], key=account_key)
        )

        if not accounts:
            raise web.HTTPNotFound()

        operations = await storage.operations.find(
            query=OperationQuery(account=accounts[0], key=operation_key)
        )

        if not operations:
            raise web.HTTPNotFound()

        response = {"operation": serialize_operation(operations[0])}

    return json_response(response)


@user_required
async def remove(request: web.Request) -> web.Response:
    account_key = get_instance_id(request, "account_key")
    operation_key = get_instance_id(request, "operation_key")

    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        accounts = await storage.accounts.find(
            query=AccountQuery(user=request["user"], key=account_key)
        )

        if not accounts:
            raise web.HTTPNotFound()

        operations = await storage.operations.find(
            query=OperationQuery(account=accounts[0], key=operation_key)
        )

        if not operations:
            raise web.HTTPNotFound()

        service = OperationsService(storage)
        await service.remove_from_account(accounts[0], operations[0])

    return web.Response(status=204)
