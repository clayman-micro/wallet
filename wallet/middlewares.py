import ujson
from aiohttp import ClientSession, web

from wallet.handlers import json_response
from wallet.storage import ResourceNotFound
from wallet.validation import ValidationError


async def catch_exceptions_middleware(app, handler):
    async def middleware_handler(request: web.Request):
        try:
            return await handler(request)
        except ResourceNotFound:
            raise web.HTTPNotFound
        except ValidationError as exc:
            return json_response(exc.errors, status=400)
        except Exception as exc:
            if isinstance(exc, (web.HTTPClientError, )):
                raise

            # send error to sentry
            if request.app.raven:
                request.app.raven.captureException()
            else:
                raise exc

            raise web.HTTPInternalServerError

    return middleware_handler


async def auth_middleware(app, handler):
    auth_service = '{}/api/identify'.format(app.config.get('passport_dsn'))

    async def middleware_handler(request: web.Request):
        token = request.headers.get('X-Access-Token', None)

        if not token:
            raise web.HTTPUnauthorized(text='Access denied')

        headers = {'X-ACCESS-TOKEN': token}
        async with ClientSession() as session:
            async with session.get(auth_service, headers=headers) as resp:
                status = resp.status
                text = await resp.text()

        if status == 200:
            try:
                data = ujson.loads(text)
            except KeyError:
                raise web.HTTPInternalServerError()
            except ValueError:
                raise web.HTTPInternalServerError()
            else:
                response = await handler(data['owner'], request)
        elif status == 401:
            raise web.HTTPUnauthorized(text=text)
        else:
            raise web.HTTPBadRequest()

        return response

    return middleware_handler
