from contextvars import ContextVar

from aiohttp import web
from aiohttp.typedefs import Handler

from wallet.web.schemas.abc import CommonParameters

schema = CommonParameters()
common_context = ContextVar("common", default=None)


@web.middleware
async def middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    common_params = schema.load(request.headers)

    common_context.set(common_params)

    if common_params["request_id"]:
        request["logger"] = request.app["logger"].bind(request_id=common_params["request_id"])

    if common_params["correlation_id"]:
        request["logger"] = request.app["logger"].bind(correlation_id=common_params["correlation_id"])

    response = await handler(request)

    return response
