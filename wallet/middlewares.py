from aiohttp import web

from wallet.adapters.owner import OwnerAdapter
from wallet.entities import EntityNotFound
from wallet.handlers import json_response
from wallet.validation import ValidationError


@web.middleware
async def catch_exceptions_middleware(request: web.Request, handler):
    try:
        return await handler(request)
    except EntityNotFound:
        raise web.HTTPNotFound
    except ValidationError as exc:
        return json_response(exc.errors, status=422)
    except Exception as exc:
        if isinstance(exc, (web.HTTPClientError, )):
            raise

        # send error to sentry
        if request.app.raven:
            request.app.raven.captureException()
        else:
            raise exc

        raise web.HTTPInternalServerError


@web.middleware
async def auth_middleware(request: web.Request, handler):
    adapter = OwnerAdapter(request.app.passport)

    token = request.headers.get('X-Access-Token', None)
    owner = await adapter.identify(token)

    response = await handler(owner, request)

    return response
