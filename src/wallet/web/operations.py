import decimal

from aiohttp import web
from aiohttp_micro.schemas import EnumField
from aiohttp_openapi import (
    JSONResponse,
    register_operation,
    RequestBody,
)
from marshmallow import fields, post_load, Schema
from passport.client import user_required

from wallet.core.entities import (
    OperationFilters,
    OperationPayload,
    OperationType,
)
from wallet.core.use_cases.operations import AddUseCase, SearchUseCase
from wallet.storage import DBStorage
from wallet.web import AccessToken, serialize, validate_payload
from wallet.web.accounts import AccountSchema
from wallet.web.categories import CategorySchema


class OperationSchema(Schema):
    key = fields.Int(required=True, data_key="id", description="Operation ID")
    amount = fields.Decimal(places=2, required=True, description="Amount")
    description = fields.Str(
        required=True, data_key="desc", description="Description"
    )
    account = fields.Nested(
        AccountSchema, required=True, description="Account",
    )
    category = fields.Nested(
        CategorySchema, required=True, description="Category",
    )
    operation_type = EnumField(
        OperationType,
        data_key="operationType",
        required=True,
        description="Operation type",
    )
    created_on = fields.DateTime(required=True, description="Created date")


class OperationsResponseSchema(Schema):
    operations = fields.List(
        fields.Nested(OperationSchema),
        required=True,
        description="Operation list",
    )


@register_operation(
    description="Show operations",
    parameters=(AccessToken,),
    responses=(
        JSONResponse(
            description="Operation list",
            schema=OperationsResponseSchema,
            status_code=200,
        ),
    ),
)
@user_required()
@serialize(OperationsResponseSchema)
async def search(request: web.Request) -> web.Response:
    search_operations = SearchUseCase(
        storage=DBStorage(request.app["db"]), logger=request.app["logger"]
    )

    return {
        "operations": [
            operation
            async for operation in search_operations.execute(
                filters=OperationFilters(user=request["user"])
            )
        ]
    }


class AddOperationPayloadSchema(Schema):
    amount = fields.Decimal(places=2, rounding=decimal.ROUND_UP, required=True)
    description = fields.Str()
    account = fields.Int(required=True)
    category = fields.Int(required=True)
    operation_type = EnumField(
        OperationType,
        missing=OperationType.expense,
        default=OperationType.expense,
    )
    created_on = fields.DateTime(required=True)

    @post_load
    def make_payload(self, data, **kwargs) -> OperationPayload:
        payload = OperationPayload(user=self.context["user"], **data)

        return payload


class OperationResponseSchema(Schema):
    operation = fields.Nested(OperationSchema, required=True)


@register_operation(
    description="Add new operation",
    parameters=(AccessToken,),
    request_body=RequestBody(
        description="Add new operation", schema=AddOperationPayloadSchema
    ),
    responses=(
        JSONResponse(
            description="Added operation",
            schema=OperationResponseSchema,
            status_code=201,
        ),
    ),
)
@user_required()
@validate_payload(AddOperationPayloadSchema, inject_user=True)
@serialize(OperationResponseSchema, status=201)
async def add(payload: OperationPayload, request: web.Request) -> web.Response:
    add_operation = AddUseCase(
        storage=DBStorage(request.app["db"]), logger=request.app["logger"]
    )
    operation = await add_operation.execute(payload=payload)

    return {"operation": operation}
