import functools

from aiohttp import web
from aiohttp.web_response import json_response
from aiohttp_openapi import Parameter, ParameterIn
from marshmallow import Schema


AccessToken = Parameter(
    in_=ParameterIn.header,
    name="X-Access-Token",
    schema={"type": "string"},
    required=True,
)


def serialize(schema_cls: Schema, status: int = 200):
    def wrapper(f):
        @functools.wraps(f)
        async def wrapped(request: web.Request, *args, **kwargs):
            response = await f(request, *args, **kwargs)

            if isinstance(response, web.Response):
                return response
            else:
                schema = schema_cls()
                return json_response(schema.dump(response), status=status)

        return wrapped

    return wrapper
