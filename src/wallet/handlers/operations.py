from aiohttp import web
from aiohttp_micro.handlers import json_response  # type:ignore
from passport.handlers.users import user_required

from wallet.domain.storage import EntityNotFound
from wallet.handlers import get_instance_id, validate_payload
from wallet.schemas import OperationSchema
from wallet.services.operations import OperationsService
from wallet.storage import DBStorage


@user_required()
@validate_payload(OperationSchema, "operation")
async def add(request: web.Request) -> web.Response:
    operation = request["operation"]

    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        try:
            account = await storage.accounts.find_by_key(
                user=request["user"],
                key=get_instance_id(request, "account_key"),
            )
        except EntityNotFound:
            raise web.HTTPNotFound()

        service = OperationsService(storage)
        await service.add_to_account(account, operation)

    schema = OperationSchema(
        only=("key", "amount", "description", "type", "created_on")
    )
    return json_response({"operation": schema.dump(operation)}, status=201)


@user_required()
async def search(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        try:
            account = await storage.accounts.find_by_key(
                user=request["user"],
                key=get_instance_id(request, "account_key"),
            )
        except EntityNotFound:
            raise web.HTTPNotFound()

        service = OperationsService(storage)
        operations = await service.fetch(account=account)

    schema = OperationSchema(
        only=("key", "amount", "description", "type", "created_on")
    )
    return json_response({"operations": schema.dump(operations, many=True)})


@user_required()
async def fetch(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        try:
            account = await storage.accounts.find_by_key(
                user=request["user"],
                key=get_instance_id(request, "account_key"),
            )
        except EntityNotFound:
            raise web.HTTPNotFound()

        service = OperationsService(storage)
        try:
            operation = await service.fetch_by_key(
                account=account, key=get_instance_id(request, "operation_key")
            )
        except EntityNotFound:
            raise web.HTTPNotFound()

    schema = OperationSchema(
        only=("key", "amount", "description", "type", "created_on")
    )
    return json_response({"operation": schema.dump(operation)})


@user_required()
async def remove(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        try:
            account = await storage.accounts.find_by_key(
                user=request["user"],
                key=get_instance_id(request, "account_key"),
            )
        except EntityNotFound:
            raise web.HTTPNotFound()

        service = OperationsService(storage)
        try:
            operation = await service.fetch_by_key(
                account=account, key=get_instance_id(request, "operation_key")
            )
        except EntityNotFound:
            raise web.HTTPNotFound()

        await service.remove_from_account(account, operation)

    return web.Response(status=204)
