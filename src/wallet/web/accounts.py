from typing import Dict

from aiohttp import web
from aiohttp_micro.web.handlers import json_response, validate_payload
from marshmallow import fields, Schema
from passport.client import user_required

from wallet.core.entities import AccountFilters, AccountPayload
from wallet.core.exceptions import AccountAlreadyExist
from wallet.core.use_cases.accounts import AddUseCase, SearchUseCase
from wallet.storage import DBStorage
from wallet.web import serialize


class BalanceSchema(Schema):
    pass


class AccountSchema(Schema):
    key = fields.Int(required=True, data_key="id", description="Account id")
    name = fields.Str(required=True, description="Account name")


class AccountsResponseSchema(Schema):
    accounts = fields.List(fields.Nested(AccountSchema), required=True, description="Accounts")


@user_required()
@serialize(AccountsResponseSchema)
async def search(request: web.Request) -> web.Response:
    search_accounts = SearchUseCase(DBStorage(request.app["db"]), logger=request.app["logger"])

    return {
        "accounts": [account async for account in search_accounts.execute(filters=AccountFilters(user=request["user"]))]
    }


class ManageAccountPayloadSchema(Schema):
    name = fields.Str(required=True, description="Account name")


class AccountResponseSchema(Schema):
    account = fields.Nested(AccountSchema, required=True)


@user_required()
@validate_payload(ManageAccountPayloadSchema)
@serialize(AccountsResponseSchema, status=201)
async def add(payload: Dict[str, str], request: web.Request) -> web.Response:
    storage = DBStorage(request.app["db"])

    try:
        add_account = AddUseCase(storage, logger=request.app["logger"])
        account = await add_account.execute(payload=AccountPayload(user=request["user"], name=payload["name"]))

        return {"account": account}
    except AccountAlreadyExist:
        return json_response({"errors": {"name": "Already exist"}}, status=422)


async def update(request: web.Request) -> web.Response:
    raise NotImplementedError()


async def remove(request: web.Request) -> web.Response:
    raise NotImplementedError()


class BalanceResponseSchema(Schema):
    balance = fields.List(fields.Nested(BalanceSchema), required=True)


async def balance(request: web.Request) -> web.Response:
    raise NotImplementedError()
