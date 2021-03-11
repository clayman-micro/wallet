import csv
import decimal
import io
from datetime import datetime
from typing import Optional, Tuple

from aiohttp import web
from aiohttp_micro.schemas import EnumField
from aiohttp_openapi import (
    JSONResponse,
    Parameter,
    ParameterIn,
    register_operation,
    RequestBody,
)
from marshmallow import fields, post_load, Schema
from passport.client import user_required

from wallet.core.entities import (
    BulkOperationsPayload,
    OperationFilters,
    OperationPayload,
    OperationType,
)
from wallet.core.use_cases.operations import (
    AddBulkUseCase,
    AddUseCase,
    SearchUseCase,
)
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
        data_key="type",
        required=True,
        description="Operation type",
    )
    created_on = fields.DateTime(
        required=True, data_key="created", description="Created date"
    )


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
        data_key="type",
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


class BulkOperationPayloadSchema(Schema):
    account = fields.Int(required=True)
    operations = fields.Str(required=True)

    def process_row(
        self, account: int, row: Tuple[str, str, str, str]
    ) -> Optional[OperationPayload]:
        raw_created, raw_amount, raw_category, description = row

        try:
            amount = decimal.Decimal(raw_amount.replace(",", "."))
        except ValueError:
            return None

        try:
            category = int(raw_category)
        except ValueError:
            category = raw_category

        operation_type = OperationType.income
        if amount < 0:
            operation_type = OperationType.expense

        try:
            created = datetime.strptime(raw_created, "%d.%m.%Y %H:%M:%S")
        except ValueError:
            try:
                created = datetime.strptime(raw_created, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                return None

        return OperationPayload(
            user=self.context["user"],
            amount=amount,
            account=account,
            category=category,
            description=description,
            operation_type=operation_type,
            created_on=created,
        )

    @post_load
    def make_payload(self, data, **kwargs) -> OperationPayload:
        account_keys = set()
        category_keys = set()
        category_names = set()
        operations = []

        for row in csv.reader(io.StringIO(data["operations"]), delimiter=","):
            operation = self.process_row(data["account"], row)

            if operation:
                account_keys.add(operation.account)

                if isinstance(operation.category, int):
                    category_keys.add(operation.category)
                elif isinstance(operation.category, str):
                    category_names.add(operation.category)
                operations.append(operation)

        return BulkOperationsPayload(
            user=self.context["user"],
            account_keys=account_keys,
            category_keys=category_keys,
            category_names=category_names,
            operations=operations,
        )


@register_operation(
    description="Bulk add operations",
    parameters=(AccessToken,),
    request_body=RequestBody(
        description="Add operations", schema=BulkOperationPayloadSchema
    ),
    responses=(
        JSONResponse(
            description="Added operations",
            schema=OperationsResponseSchema,
            status_code=201,
        ),
    ),
)
@user_required()
@validate_payload(BulkOperationPayloadSchema, inject_user=True)
@serialize(OperationsResponseSchema, status=201)
async def add_bulk(
    payload: BulkOperationsPayload, request: web.Request
) -> web.Response:
    add_operations = AddBulkUseCase(
        storage=DBStorage(request.app["db"]), logger=request.app["logger"]
    )

    return {
        "operations": [
            operation
            async for operation in add_operations.execute(payload=payload)
        ]
    }
