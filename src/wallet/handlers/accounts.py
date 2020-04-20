from aiohttp import web
from aiohttp_micro.handlers import json_response  # type:ignore
from passport.handlers.users import user_required

from wallet.domain.storage import EntityAlreadyExist, EntityNotFound
from wallet.handlers import get_instance_id, validate_payload
from wallet.schemas import AccountSchema, BalanceSchema
from wallet.services.accounts import AccountsService
from wallet.storage import DBStorage


@user_required()
@validate_payload(AccountSchema, "account")
async def register(request: web.Request) -> web.Response:
    account = request["account"]

    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        try:
            service = AccountsService(storage)
            await service.register(account)
        except EntityAlreadyExist:
            return json_response(
                {"errors": {"name": "Already exist"}}, status=422
            )

    schema = AccountSchema(only=("key", "name", "latest_balance"))
    return json_response({"account": schema.dump(account)}, status=201)


@user_required()
async def search(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)
        accounts = await storage.accounts.find(user=request["user"])

    schema = AccountSchema(only=("key", "name", "latest_balance"))
    return json_response({"accounts": schema.dump(accounts, many=True)})


@user_required()
async def balance(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        try:
            account = await storage.accounts.find_by_key(
                user=request["user"],
                key=get_instance_id(request, "account_key"),
            )
        except EntityNotFound:
            raise web.HTTPNotFound()

    schema = BalanceSchema(exclude=("key",))
    return json_response({"balance": schema.dump(account.balance, many=True)})


@user_required()
@validate_payload(AccountSchema, "account")
async def update(request: web.Request) -> web.Response:
    next_account = request["account"]

    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        try:
            account = await storage.accounts.find_by_key(
                user=request["user"],
                key=get_instance_id(request, "account_key"),
            )
        except EntityNotFound:
            raise web.HTTPNotFound()

        if next_account.name:
            account.name = next_account.name
            await storage.accounts.update(account, fields=("name",))

    return web.Response(status=204)


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

        await storage.accounts.remove(account)

    return web.Response(status=204)
