from http import HTTPStatus
from typing import Dict

from aiohttp import web
from aiohttp_micro.web.handlers import json_response
from aiohttp_micro.web.handlers.openapi import OpenAPISpec, PayloadSchema, ResponseSchema
from marshmallow import fields, Schema
from passport.client import user_required

from wallet.core.entities import AccountFilters, AccountPayload
from wallet.core.exceptions import AccountAlreadyExist
from wallet.core.use_cases.accounts import AddUseCase, SearchUseCase
from wallet.storage import DBStorage
from wallet.web import CollectionFiltersSchema, CommonParameters, serialize, validate_payload


class BalanceSchema(Schema):
    pass


class AccountSchema(Schema):
    key = fields.Int(required=True, data_key="id", dump_only=True, description="Account id")
    name = fields.Str(required=True, description="Account name")


class AccountsResponseSchema(ResponseSchema):
    """Accounts list."""

    accounts = fields.List(fields.Nested(AccountSchema), required=True, description="Accounts")


class AccountsFilterSchema(CollectionFiltersSchema):
    """Filter accounts list."""


@user_required()
@serialize(AccountsResponseSchema)
async def search(request: web.Request) -> web.Response:
    """Get accounts list."""

    search_accounts = SearchUseCase(DBStorage(request.app["db"]), logger=request.app["logger"])
    accounts_stream = search_accounts.execute(filters=AccountFilters(user=request["user"]))

    return {"accounts": [account async for account in accounts_stream]}


search.spec = OpenAPISpec(
    operation="getAccounts",
    parameters=[CommonParameters, AccountsFilterSchema],
    responses={
        HTTPStatus.OK: AccountsResponseSchema,
        # HTTPStatus.UNAUTHORIZED: ErrorSchema,
        # HTTPStatus.FORBIDDEN: ErrorSchema,
    },
    security="TokenAuth",
    tags=["accounts"],
)


class ManageAccountPayloadSchema(PayloadSchema):
    """Add new account."""

    name = fields.Str(required=True, description="Account name")


class AccountResponseSchema(ResponseSchema):
    """Get account info."""

    account = fields.Nested(AccountSchema, required=True, description="Account info")


@user_required()
@validate_payload(ManageAccountPayloadSchema)
@serialize(AccountsResponseSchema, status=201)
async def add(payload: Dict[str, str], request: web.Request) -> web.Response:
    """Add new account."""

    storage = DBStorage(request.app["db"])

    try:
        add_account = AddUseCase(storage, logger=request.app["logger"])
        account = await add_account.execute(payload=AccountPayload(user=request["user"], name=payload["name"]))

        return {"account": account}
    except AccountAlreadyExist:
        return json_response({"errors": {"name": "Already exist"}}, status=422)


add.spec = OpenAPISpec(
    operation="addAccount",
    parameters=[CommonParameters],
    payload=ManageAccountPayloadSchema,
    responses={
        HTTPStatus.CREATED: AccountResponseSchema,
        # HTTPStatus.UNAUTHORIZED: ErrorSchema,
        # HTTPStatus.FORBIDDEN: ErrorSchema,
    },
    security="TokenAuth",
    tags=["accounts"],
)


async def update(request: web.Request) -> web.Response:
    raise NotImplementedError()


async def remove(request: web.Request) -> web.Response:
    raise NotImplementedError()


class BalanceResponseSchema(Schema):
    balance = fields.List(fields.Nested(BalanceSchema), required=True)


async def balance(request: web.Request) -> web.Response:
    raise NotImplementedError()
