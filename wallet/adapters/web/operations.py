from typing import Any, Dict

from aiohttp import web

from wallet.adapters.web import get_instance_id, get_payload, json_response
from wallet.adapters.web.accounts import get_account
from wallet.adapters.web.users import user_required
from wallet.domain.entities import Account, Operation
from wallet.domain.storage import OperationQuery
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
    validator = OperationValidator()

    payload = await get_payload(request)
    document = validator.validate_payload(payload)

    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        account = await get_account(request, storage, "account_key")

        service = OperationsService(storage)
        operation = await service.add_to_account(
            account=account,
            amount=document["amount"],
            description=document.get("description", ""),
            operation_type=document["type"],
            created_on=document["created_on"],
        )

    return json_response({"operation": serialize_operation(operation)}, status=201)


@user_required
async def search(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        account = await get_account(request, storage, "account_key")

        query = OperationQuery(account=account)
        operations = await storage.operations.find(query=query)

    return json_response(
        {"operations": [serialize_operation(operation) for operation in operations]}
    )


async def get_operation(
    request: web.Request, storage: DBStorage, account: Account, key: str
) -> Operation:
    query = OperationQuery(account=account, key=get_instance_id(request, key))
    operations = await storage.operations.find(query=query)

    if not operations:
        raise web.HTTPNotFound()

    return operations[0]


@user_required
async def fetch(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        account = await get_account(request, storage, "account_key")
        operation = await get_operation(request, storage, account, "operation_key")

    return json_response({"operation": serialize_operation(operation)})


@user_required
async def remove(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        account = await get_account(request, storage, "account_key")
        operation = await get_operation(request, storage, account, "operation_key")

        service = OperationsService(storage)
        await service.remove_from_account(account, operation)

    return web.Response(status=204)
