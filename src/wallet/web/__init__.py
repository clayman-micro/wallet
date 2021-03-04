import functools
from typing import Any, Dict, Generic, Type, TypeVar

import ujson
from aiohttp import web
from aiohttp.web_response import json_response
from aiohttp_micro.handlers import get_payload
from aiohttp_openapi import Parameter, ParameterIn
from marshmallow import post_load, Schema, ValidationError

from wallet.core.entities import Payload  # noqa: F401


AccessToken = Parameter(
    in_=ParameterIn.header,
    name="X-Access-Token",
    schema={"type": "string"},
    required=True,
)


PT = TypeVar("PT", bound="Payload")


class PayloadSchema(Schema, Generic[PT]):
    payload_cls: Type[PT]

    @post_load
    def build_payload(self, payload: Dict[str, Any], **kwargs) -> PT:
        return self.payload_cls(**payload)


def validate_payload(schema_cls: Type[Schema], inject_user: bool = False):
    def wrapper(f):
        async def wrapped(request: web.Request) -> web.Response:
            payload = await get_payload(request)

            try:
                schema = schema_cls()

                if inject_user:
                    schema.context["user"] = request["user"]

                document = schema.load(payload)
            except ValidationError as exc:
                return json_response({"errors": exc.messages}, status=422)

            return await f(document, request)

        return wrapped

    return wrapper


def serialize(schema_cls: Schema, status: int = 200):
    def wrapper(f):
        @functools.wraps(f)
        async def wrapped(request: web.Request, *args, **kwargs):
            response = await f(request, *args, **kwargs)

            if isinstance(response, web.Response):
                return response
            else:
                schema = schema_cls()
                return json_response(
                    schema.dump(response), status=status, dumps=ujson.dumps
                )

        return wrapped

    return wrapper
