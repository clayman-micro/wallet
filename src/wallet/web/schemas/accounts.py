from aiohttp_micro.web.handlers.openapi import PayloadSchema, ResponseSchema
from marshmallow import fields, post_load, Schema

from wallet.core.entities.accounts import AccountFilters
from wallet.web.schemas.abc import CollectionFiltersSchema


class AccountSchema(Schema):
    key = fields.Int(required=True, data_key="id", dump_only=True, description="Account id")
    name = fields.Str(required=True, description="Account name")


class AccountsResponseSchema(ResponseSchema):
    """Accounts list."""

    accounts = fields.List(fields.Nested(AccountSchema), required=True, description="Accounts")


class AccountsFilterSchema(CollectionFiltersSchema):
    """Filter accounts list."""

    @post_load
    def make_payload(self, data, **kwargs):
        return AccountFilters(user=self.context["user"])


class ManageAccountPayloadSchema(PayloadSchema):
    """Add new account."""

    name = fields.Str(required=True, description="Account name")


class AccountResponseSchema(ResponseSchema):
    """Get account info."""

    account = fields.Nested(AccountSchema, required=True, description="Account info")
