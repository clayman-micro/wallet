from typing import Any, Dict

from aiohttp import web

from wallet.adapters.web import get_instance_id, get_payload, json_response
from wallet.adapters.web.users import user_required
from wallet.domain import Account
from wallet.domain.storage import EntityAlreadyExist, EntityNotFound
from wallet.services.accounts import AccountsService, AccountValidator
from wallet.storage import DBStorage
from wallet.validation import ValidationError


def serialize_account(instance: Account) -> Dict[str, Any]:
    balance = instance.balance[0]

    return {
        "id": instance.key,
        "name": instance.name,
        "balance": {
            "incomes": float(balance.incomes),
            "expenses": float(balance.expenses),
            "rest": float(balance.rest),
        },
    }


@user_required
async def register(request: web.Request) -> web.Response:
    validator = AccountValidator()

    payload = await get_payload(request)
    document = validator.validate_payload(payload)

    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        try:
            service = AccountsService(storage)
            account = await service.register(name=document["name"], user=request["user"])
        except EntityAlreadyExist:
            raise ValidationError({"name": "Already exist"})

    return json_response({"account": serialize_account(account)}, status=201)


@user_required
async def search(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)
        accounts = await storage.accounts.find(user=request.get('user'))

    return json_response({"accounts": [serialize_account(account) for account in accounts]})


async def get_account(request: web.Request, storage: DBStorage, key: str) -> Account:
    try:
        account = await storage.accounts.find_by_key(
            user=request.get("user"),
            key=get_instance_id(request, key)
        )
    except EntityNotFound:
        raise web.HTTPNotFound()

    return account


@user_required
async def balance(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        account = await get_account(request, storage, "account_key")

    response = {
        "balance": [
            {
                "incomes": float(item.incomes),
                "expenses": float(item.expenses),
                "rest": float(item.rest),
                "month": item.month.strftime("%Y-%m-%d"),
            }
            for item in account.balance
        ]
    }

    return json_response(response)


@user_required
async def update(request: web.Request) -> web.Response:
    validator = AccountValidator()

    payload = await get_payload(request)
    document = validator.validate_payload(payload)

    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        account = await get_account(request, storage, "account_key")
        if "name" in document:
            account.name = document["name"]
            await storage.accounts.update(account, fields=("name",))

    return web.Response(status=204)


@user_required
async def remove(request: web.Request) -> web.Response:
    async with request.app["db"].acquire() as conn:
        storage = DBStorage(conn)

        account = await get_account(request, storage, "account_key")
        await storage.accounts.remove(account)

    return web.Response(status=204)
