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

            if 'raven' in request.app:
                # send error to sentry
                request.app['raven'].captureException()
            return internal_error

        if isinstance(response, web.Response):
            return response

        return json_response(response)
    return wrapper


async def create_resource(request, table, schema, validate, **kwargs):
    payload = await get_payload(request)
    document = validate_payload(payload, schema)

    if callable(validate):
        document = await validate(document, request, **kwargs)

    return await create_instance(document, table, engine=request.app['engine'])


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
def get_collection(name: str, serialize=serialize):
    def decorator(f):
        @functools.wraps(f)
        @handle_response
        async def wrapped(*args, **kwargs):
            request = args[-1]
            query, total_query = await f(*args, **kwargs)

            collection = []
            total = 0
            async with request.app['engine'].acquire() as conn:
                result = await conn.execute(query)

                if result.returns_rows:
                    rows = await result.fetchall()
                    collection = list(map(
                        serialize,
                        map(lambda row: dict(zip(row.keys(), row.values())), rows)
                    ))

                if total_query is not None:
                    total = await conn.scalar(total_query)

            return {
                name: collection,
                'meta': {
                    'total': total,
                    'count': len(collection)
                }
            }
        return wrapped
    return decorator


class BaseHandler(object):
    decorators = tuple()
    endpoints = tuple()

    async def get_payload(self, request: web.Request) -> dict:
        if 'application/json' in request.headers.get('CONTENT-TYPE'):
            payload = await request.json()
        else:
            payload = await request.post()
        return dict(payload)

    def response(self, content: str, **kwargs) -> web.Response:
        return web.Response(body=content.encode('utf-8'), **kwargs)

    def json_response(self, content: dict, **kwargs) -> web.Response:
        kwargs.setdefault('content_type', 'application/json')
        return self.response(ujson.dumps(content), **kwargs)


class ResourceHandler(BaseHandler):
    resource_name = ''
    resource_key = 'instance_id'

    table = None  # type: Table
    schema = None  # type: Dict

    def serialize(self, resource):
        return {key: value for key, value in iter(resource.items())}

    def get_resource_query(self, request: web.Request, **kwargs):
        instance_id = get_instance_id(request, self.resource_key)
        return select([self.table]).where(self.table.c.id == instance_id)

    async def get_resource(self, request: web.Request, **kwargs):
        query = self.get_resource_query(request, **kwargs)
        resource = await get_instance(request.app['engine'], query)

        if not resource:
            raise web.HTTPNotFound()
        return resource

    async def get(self, request: web.Request, **kwargs):
        instance = await self.get_resource(request, **kwargs)
        return {self.resource_name: self.serialize(instance)}

    async def validate(self, document: Dict, request: web.Request, **kwargs):
        return document

    async def after_create(self, resource, request: web.Request, **kwargs):
        pass

    async def post(self, request: web.Request, **kwargs):
        payload = await self.get_payload(request)

        # Common validation logic
        validator = CustomValidator(schema=self.schema)
        if not validator.validate(payload):
            raise ValidationError(validator.errors)

        document = await self.validate(validator.document, request, **kwargs)

        document['id'] = await create_instance(request.app['engine'],
                                               self.table, document)

        await self.after_create(document, request, **kwargs)

        return self.json_response({
            self.resource_name: self.serialize(document)
        }, status=201)

    async def after_update(self, resource, request: web.Request, **kwargs):
        return resource

    async def put(self, request: web.Request, **kwargs):
        instance = await self.get_resource(request, **kwargs)

        payload = await self.get_payload(request)
        validator = CustomValidator(schema=self.schema, allow_unknown=True)
        if not validator.validate(payload, update=True):
            raise ValidationError(validator.errors)

        before = instance.copy()
        instance.update(validator.document)
        instance = await self.validate(instance, request,
                                       instance=instance, **kwargs)

        # Update row in database
        try:
            await update_instance(request.app['engine'], self.table, instance)
        except DatabaseError as exc:
            raise

        instance = await self.after_update(instance, request, before=before,
                                           **kwargs)
        return {
            self.resource_name: self.serialize(instance)
        }

    async def after_remove(self, resource, request: web.Request, **kwargs):
        pass

    async def delete(self, request: web.Request, **kwargs):
        resource = await self.get_resource(request, **kwargs)

        try:
            await remove_instance(request.app['engine'], self.table, resource)
        except DatabaseError as exc:
            if 'integrity_error' in exc.errors:
                raise web.HTTPBadRequest(text='Could not be removed')
            raise

        await self.after_remove(resource, request, **kwargs)

        return {self.resource_name: {'status': 'removed'}}
