from aiohttp import web
from sentry_sdk import capture_exception

from wallet.adapters.web import Handler, json_response
from wallet.validation import ValidationError


@web.middleware
async def catch_exceptions_middleware(request: web.Request, handler: Handler) -> web.Response:
    try:
        return await handler(request)
    except ValidationError as exc:
        return json_response(exc.errors, status=422)
    except Exception as exc:
        capture_exception(exc)

        if isinstance(exc, (web.HTTPClientError,)):
            raise

        raise web.HTTPInternalServerError


async def index(request: web.Request) -> web.Response:
    return json_response(
        {
            "project": request.app["distribution"].project_name,
            "version": request.app["distribution"].version,
        }
    )


async def health(request: web.Request) -> web.Response:
    return web.Response(body=b"Healthy")
