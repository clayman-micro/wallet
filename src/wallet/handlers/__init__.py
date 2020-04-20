from typing import Awaitable, Callable, Type

from aiohttp import web
from aiohttp_micro.handlers import get_payload, json_response
from marshmallow import ValidationError

from wallet.schemas import Schema


Handler = Callable[[web.Request], Awaitable[web.Response]]


def get_instance_id(request, key="instance_id"):
    if key not in request.match_info:
        raise web.HTTPInternalServerError(text="`%s` could not be found" % key)

    try:
        instance_id = int(request.match_info[key])
    except ValueError:
        raise web.HTTPBadRequest(
            text="`%s` should be numeric" % request.match_info[key]
        )

    return instance_id


def validate_payload(schema_cls: Type[Schema], entity_name: str):
    def wrapper(f):
        async def wrapped(request: web.Request) -> web.Response:
            payload = await get_payload(request)

            schema = schema_cls()
            if "user" in request:
                schema.context = {"user": request["user"]}

            try:
                entity = schema.load(payload)
            except ValidationError as exc:
                return json_response({"errors": exc.messages}, status=422)

            request["schema"] = schema
            request[entity_name] = entity

            return await f(request)

        return wrapped

    return wrapper
