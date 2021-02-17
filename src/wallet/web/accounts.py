from typing import Dict

from aiohttp import web
from aiohttp_micro.handlers import json_response, validate_payload
from aiohttp_openapi import (
    JSONResponse,
    Parameter,
    ParameterIn,
    register_operation,
    RequestBody,
)
from marshmallow import fields, Schema
from passport.client import user_required

from wallet.core.entities import AccountFilters, AccountPayload
from wallet.core.exceptions import AccountAlreadyExist
from wallet.core.use_cases.accounts import AddUseCase, SearchUseCase
from wallet.storage import DBStorage
from wallet.web import AccessToken


AccountKey = Parameter(
    in_=ParameterIn.path,
    name="account_key",
    schema={"type": "integer"},
    required=True,
)


class BalanceSchema(Schema):
    pass


class AccountSchema(Schema):
    key = fields.Int(required=True, data_key="id", description="Account id")
    name = fields.Str(required=True, description="Account name")


class AccountsResponseSchema(Schema):
    accounts = fields.List(
        fields.Nested(AccountSchema), required=True, description="Accounts"
    )


@register_operation(
    description="Show available accounts",
    parameters=(AccessToken,),
    responses=(
        JSONResponse(
            description="Accounts list",
            schema=AccountsResponseSchema,
            status_code=200,
        ),
    ),
)
@user_required()
async def search(request: web.Request) -> web.Response:
    storage = DBStorage(request.app["db"])

    filters = AccountFilters(user=request["user"])

    use_case = SearchUseCase(storage, logger=request.app["logger"])
    accounts = [account async for account in use_case.execute(filters=filters)]

    schema = AccountsResponseSchema()
    return json_response(schema.dump({"accounts": accounts}))


class ManageAccountPayloadSchema(Schema):
    name = fields.Str(required=True, description="Account name")


class AccountResponseSchema(Schema):
    account = fields.Nested(AccountSchema, required=True)


@register_operation(
    description="Add new account",
    parameters=(AccessToken,),
    request_body=RequestBody(
        description="Add new account", schema=ManageAccountPayloadSchema
    ),
    responses=(
        JSONResponse(
            description="Added account",
            schema=AccountResponseSchema,
            status_code=201,
        ),
    ),
)
@user_required()
@validate_payload(ManageAccountPayloadSchema)
async def add(payload: Dict[str, str], request: web.Request) -> web.Response:
    storage = DBStorage(request.app["db"])

    try:
        use_case = AddUseCase(storage, logger=request.app["logger"])
        account = await use_case.execute(
            payload=AccountPayload(user=request["user"], name=payload["name"])
        )
    except AccountAlreadyExist:
        return json_response({"errors": {"name": "Already exist"}}, status=422)

    schema = AccountResponseSchema()
    return json_response(schema.dump({"account": account}), status=201)


@register_operation(
    description="Update existed account",
    parameters=(AccessToken, AccountKey),
    request_body=RequestBody(
        description="Update account", schema=ManageAccountPayloadSchema
    ),
    responses=(
        JSONResponse(
            description="Updated account",
            schema=AccountResponseSchema,
            status_code=201,
        ),
    ),
)
async def update(request: web.Request) -> web.Response:
    raise NotImplementedError()


@register_operation(
    description="Remove account",
    parameters=(AccessToken, AccountKey),
    responses=(
        JSONResponse(
            description="Remove account", schema=Schema, status_code=200,
        ),
    ),
)
async def remove(request: web.Request) -> web.Response:
    raise NotImplementedError()


class BalanceResponseSchema(Schema):
    balance = fields.List(fields.Nested(BalanceSchema), required=True)


@register_operation(
    description="Fetch account balance",
    parameters=(AccessToken, AccountKey),
    responses=(
        JSONResponse(
            description="Remove account",
            schema=BalanceResponseSchema,
            status_code=200,
        ),
    ),
)
async def balance(request: web.Request) -> web.Response:
    raise NotImplementedError()
