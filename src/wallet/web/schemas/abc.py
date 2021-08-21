from typing import Any, Dict, Generic, Type, TypeVar

from aiohttp_micro.core.schemas import JSON
from aiohttp_micro.web.handlers.openapi import ParameterIn, ParametersSchema, ResponseSchema
from marshmallow import EXCLUDE, fields, post_dump, post_load, Schema

from wallet.core.entities.abc import Payload


class CommonParameters(ParametersSchema):
    in_ = ParameterIn.header

    request_id = fields.Str(missing=None, data_key="X-Request-ID", description="Incoming request ID")
    correlation_id = fields.Str(missing=None, data_key="X-Correlation-ID", description="Incoming parent request ID")

    class Meta:
        unknown = EXCLUDE


class CollectionFiltersSchema(ParametersSchema):
    """Collection filters."""

    in_ = ParameterIn.query

    offset = fields.Int(
        default=0, missing=0, validate=lambda offset: offset >= 0, description="Offset from collection beginning"
    )
    limit = fields.Int(
        default=10, missing=10, validate=lambda limit: 10 <= limit <= 50, description="Number of items per page"
    )

    class Meta:
        unknown = EXCLUDE

    @post_dump
    def cleanup(self, obj: JSON, **kwargs) -> JSON:
        drop_keys = [key for key, value in obj.items() if value is None]

        for key in drop_keys:
            del obj[key]

        return obj


class ErrorResponseSchema(ResponseSchema):
    code = fields.Str(description="Error code")
    message = fields.Str(description="Error description")


PT = TypeVar("PT", bound="Payload")


class PayloadSchema(Schema, Generic[PT]):
    payload_cls: Type[PT]

    @post_load
    def build_payload(self, payload: Dict[str, Any], **kwargs) -> PT:
        return self.payload_cls(**payload)
