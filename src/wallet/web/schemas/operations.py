import decimal
from dataclasses import asdict

from aiohttp_micro.core.schemas import EnumField, JSON
from aiohttp_micro.web.handlers.openapi import PayloadSchema, ResponseSchema
from marshmallow import fields, post_load, Schema, validates_schema
from marshmallow.decorators import pre_dump

from wallet.core.entities.abc import Period
from wallet.core.entities.operations import OperationFilters, OperationPayload, OperationType
from wallet.core.exceptions import ValidationError
from wallet.web.schemas.abc import CollectionFiltersSchema
from wallet.web.schemas.accounts import AccountSchema
from wallet.web.schemas.categories import CategorySchema


class PartialAccountSchema(AccountSchema):
    class Meta:
        fields = ("key",)


class PartialCategorySchema(CategorySchema):
    class Meta:
        fields = ("key",)


class OperationSchema(Schema):
    """Operation info."""

    key = fields.Int(required=True, data_key="id", description="Operation ID")
    amount = fields.Str(places=2, required=True, description="Amount")
    description = fields.Str(required=True, data_key="desc", description="Description")
    account = fields.Nested(PartialAccountSchema, required=True, description="Account",)
    category = fields.Nested(PartialCategorySchema, required=True, description="Category",)
    operation_type = EnumField(OperationType, data_key="type", required=True, description="Operation type",)
    created_on = fields.DateTime(required=True, data_key="created", description="Created date")


class OperationsFilterSchema(CollectionFiltersSchema):
    """Filter operations list."""

    beginning = fields.Date(data_key="from", description="Period beginning")
    ending = fields.Date(data_key="to", description="Period ending")
    account_key = fields.Int(data_key="account", description="Account")
    category_key = fields.Int(data_key="category", description="Category")

    @validates_schema
    def validate_dates(self, data, **kwargs):
        beginnig = data.get("beginning", None)
        ending = data.get("ending", None)

        if beginnig and not ending:
            raise ValidationError(errors={"period": "Pediod ending requied"})
        elif ending and not beginnig:
            raise ValidationError(errors={"period": "Period beginning required"})
        elif beginnig and ending:
            if beginnig > ending:
                raise ValidationError(errors={"period": "Beginning must be earlier than ending"})

    @post_load
    def make_payload(self, data, **kwargs):
        period = None
        if "beginning" in data and "ending" in data:
            period = Period(beginning=data.pop("beginning"), ending=data.pop("ending"))

        return OperationFilters(user=self.context["user"], period=period, **data)

    @pre_dump
    def serialize_filters(self, filters: OperationFilters, **kwargs) -> JSON:
        serialized = asdict(filters)

        if filters.period:
            serialized.update({"beginning": filters.period.beginning, "ending": filters.period.ending})

        return serialized


class OperationsMetaSchema(Schema):
    filters = fields.Nested(OperationsFilterSchema, description="Filters")


class OperationsResponseSchema(ResponseSchema):
    """Operations list."""

    operations = fields.List(fields.Nested(OperationSchema), required=True, description="Operation list")
    meta = fields.Nested(OperationsMetaSchema, required=True, description="Response meta")


class ErrorsResponseSchema(ResponseSchema):
    """Errors schema"""

    errors = fields.List(fields.Dict())


class AddOperationPayloadSchema(PayloadSchema):
    """Add new operation."""

    amount = fields.Decimal(places=2, rounding=decimal.ROUND_UP, required=True)
    description = fields.Str()
    account = fields.Int(required=True)
    category = fields.Int(required=True)
    operation_type = EnumField(
        OperationType, missing=OperationType.expense, default=OperationType.expense, data_key="type",
    )
    created_on = fields.DateTime(required=True)

    @post_load
    def make_payload(self, data, **kwargs) -> OperationPayload:
        payload = OperationPayload(user=self.context["user"], **data)

        return payload


class OperationResponseSchema(ResponseSchema):
    """Get operation info."""

    operation = fields.Nested(OperationSchema, required=True)
