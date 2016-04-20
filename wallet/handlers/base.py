import functools
from typing import Dict

from aiohttp import web
from sqlalchemy import select
import ujson

from .. import exceptions
from ..storage.base import (serialize, CustomValidator,
                            create_instance, get_instance, remove_instance,
                            update_instance)


def response(content: str, **kwargs) -> web.Response:
    return web.Response(body=content.encode('utf-8'), **kwargs)


def json_response(data: dict, **kwargs) -> web.Response:
    kwargs.setdefault('content_type', 'application/json')
    return web.Response(body=ujson.dumps(data).encode('utf-8'), **kwargs)


def get_instance_id(request, key='instance_id'):
    if key not in request.match_info:
        raise web.HTTPInternalServerError(text='`%s` could not be found' % key)

    try:
        instance_id = int(request.match_info[key])
    except ValueError:
        raise web.HTTPBadRequest(
            text='`%s` should be numeric' % request.match_info[key])

    return instance_id


async def get_payload(request: web.Request) -> Dict:
    """
    Extract payload from request by Content-Type in headers.

    Method is a coroutine.
    """
    if 'application/json' in request.content_type:
        payload = await request.json()
    else:
        payload = await request.post()
    return dict(payload)


def validate_payload(payload: Dict, schema: Dict, update: bool=False) -> Dict:
    validator = CustomValidator(schema=schema, allow_unknown=update)
    if not validator.validate(payload, update=update):
        raise exceptions.ValidationError(validator.errors)

    return validator.document


def handle_response(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        internal_error = json_response({
            'errors': {'server': 'Internal error'}
        }, status=500)

        request = args[-1]

        try:
            response = await f(*args, **kwargs)
        except exceptions.ValidationError as exc:
            return json_response({'errors': exc.errors}, status=400)
        except exceptions.ResourceNotFound as exc:
            raise web.HTTPNotFound
        except Exception as exc:
            if isinstance(exc, (web.HTTPClientError, )):
                raise

            raise
            # if 'raven' in request.app:
            #     # send error to sentry
            #     request.app['raven'].captureException()
            # return internal_error

        if isinstance(response, web.Response):
            return response

        return json_response(response)
    return wrapper


async def create_resource(request, table, schema, validate, **kwargs):
    payload = await get_payload(request)
    document = validate_payload(payload, schema)

    if callable(validate):
        document = await validate(document, request, **kwargs)

    async with request.app['engine'].acquire() as conn:
        return await create_instance(document, table, conn)


def create_handler(resource_name, table, schema, validate, serialize):
    def decorator(f):
        @functools.wraps(f)
        @handle_response
        async def handler(*args, **kwargs):
            request = args[0]

            resource = await create_resource(request, table, schema, validate,
                                             **kwargs)

            if callable(f):
                resource = await f(resource, *args, **kwargs)

            return json_response({
                resource_name: serialize(resource)
            }, status=201)
        return handler
    return decorator
