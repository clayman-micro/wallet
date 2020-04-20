from datetime import datetime
from enum import Enum
from typing import Dict, List, Type, TypeVar, Union

import attr
from marshmallow import (
    fields,
    post_dump,
    post_load,
    pre_dump,
    Schema,
    ValidationError,
)

from wallet.domain import (
    Account,
    Balance,
    Entity,
    Operation,
    OperationType,
    Tag,
)


E = TypeVar("E", bound=Entity)

JSON_TOKEN = Union[str, int, float, bool, None]
JSON = Dict[str, Union[JSON_TOKEN, List[JSON_TOKEN], "JSON"]]  # noqa T484


class EntitySchema(Schema):
    entity_cls: Type[Entity]

    key = fields.Int(data_key="id", default=0)

    @post_load
    def build_entity(self, payload: JSON, **kwargs) -> E:
        return self.entity_cls(**payload)

    @pre_dump
    def serialize_entity(self, entity: E, **kwargs) -> JSON:
        if isinstance(entity, self.entity_cls):
            return attr.asdict(entity)
        else:
            return entity

    @post_dump
    def cleanup(self, obj: JSON, **kwargs) -> JSON:
        drop_keys = [key for key, value in obj.items() if value is None]

        for key in drop_keys:
            del obj[key]

        return obj


class EnumField(fields.Field):
    def __init__(self, enum_cls: Type[Enum], **kwargs) -> None:
        super().__init__(**kwargs)
        self.enum_cls = enum_cls

    def _serialize(self, value, attr, obj, **kwargs):
        if isinstance(value, self.enum_cls):
            return value.value
        return None

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return self.enum_cls(value)
        except ValueError:
            try:
                normalized = int(value)
            except ValueError:
                raise ValidationError("Invalid value", attr, value)

            try:
                return self.enum_cls(normalized)
            except ValueError:
                raise ValidationError("Invalid value", attr, value)


class BalanceSchema(EntitySchema):
    entity_cls = Balance

    rest = fields.Decimal(places=2)
    expenses = fields.Decimal(places=2)
    incomes = fields.Decimal(places=2)
    month = fields.Date(format="%Y-%m")


class AccountSchema(EntitySchema):
    entity_cls = Account

    name = fields.Str(requied=True)
    balance = fields.List(fields.Nested(BalanceSchema))
    latest_balance = fields.Method("get_latest_balance")

    def get_latest_balance(self, obj: Account):
        if len(obj["balance"]) > 0:
            balance = obj["balance"][0]

            schema = BalanceSchema(exclude=("key",))
            return schema.dump(balance)

        return {}

    @post_load
    def build_entity(self, payload: JSON, **kwargs) -> E:
        payload.setdefault("key", 0)
        payload.setdefault("user", self.context.get("user", None))

        return self.entity_cls(**payload)


class TagSchema(EntitySchema):
    entity_cls = Tag

    name = fields.Str(required=True)


class OperationSchema(EntitySchema):
    entity_cls = Operation

    amount = fields.Decimal(places=2, required=True)
    account = fields.Nested(AccountSchema, default=None)
    description = fields.Str()
    type = EnumField(OperationType, default=OperationType.expense)  # noqa: T002
    tags = fields.List(fields.Nested(TagSchema))
    created_on = fields.DateTime(format="iso")

    @post_load
    def build_entity(self, payload: JSON, **kwargs) -> E:
        payload.setdefault("key", 0)
        payload.setdefault("account", None)
        payload.setdefault("type", OperationType.expense)
        payload.setdefault("created_on", datetime.now())

        return self.entity_cls(**payload)
