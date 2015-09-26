import asyncio
import functools
from cerberus import Validator
from psycopg2 import ProgrammingError, IntegrityError
from aiohttp import web
import ujson


@asyncio.coroutine
def get_payload(request):
    if 'application/json' in request.headers.get('CONTENT-TYPE'):
        payload = yield from request.json()
    else:
        payload = yield from request.post()
    return dict(payload)


def json_response(data, **kwargs):
    kwargs.setdefault('content_type', 'application/json')
    return web.Response(body=ujson.dumps(data).encode('utf-8'), **kwargs)


def reverse_url(request, route, parts=None):
    if not parts:
        path = request.app.router[route].url()
    else:
        path = request.app.router[route].url(parts=parts)

    return '{scheme}://{host}{path}'.format(scheme=request.scheme,
                                            host=request.host, path=path)


def allow_cors(headers=None, methods=None):
    def decorator(f):
        @asyncio.coroutine
        @functools.wraps(f)
        def wrapper(*args):
            if asyncio.iscoroutinefunction(f):
                coro = f
            else:
                coro = asyncio.coroutine(f)
            request = args[-1]

            exclude_headers = set(name.upper() for name in {
                'Cache-Control', 'Content-Language', 'Content-Type', 'Expires',
                'Last-Modified', 'Pragma', 'Content-Length'
            })

            allow_methods = ['OPTIONS']
            if methods:
                allow_methods.extend([name.upper() for name in methods])

            response = yield from coro(*args)

            response.headers.update({
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Request-Method': ', '.join(allow_methods)
            })

            if 'Origin' in request.headers:
                response.headers.update({
                    'Access-Control-Allow-Origin': request.headers['Origin']
                })

                expose_headers = {name for name in response.headers
                                  if name.upper() not in exclude_headers}
                if expose_headers:
                    response.headers.update({
                        'Access-Control-Expose-Headers': ', '.join(
                            expose_headers)
                    })

                if 'Access-Control-Request-Headers' in request.headers:
                    response.headers.update({
                        'Access-Control-Allow-Headers': request.headers.get(
                            'Access-Control-Request-Headers')
                    })
            return response
        return wrapper
    return decorator


class BaseHandler(object):
    decorators = tuple()
    endpoints = tuple()

    @asyncio.coroutine
    def get_payload(self, request):
        if 'application/json' in request.headers.get('CONTENT-TYPE'):
            payload = yield from request.json()
        else:
            payload = yield from request.post()
        return dict(payload)

    def response(self, content, **kwargs):
        return web.Response(body=content.encode('utf-8'), **kwargs)

    def json_response(self, content, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        return self.response(ujson.dumps(content), **kwargs)


class BaseAPIHandler(BaseHandler):
    limit = None

    collection_name = ''
    resource_name = ''

    table = None
    schema = None
    serializer = None

    def get_collection_query(self, request):
        return self.table.select()

    def get_instance_query(self, request, instance_id):
        return self.table.select().where(self.table.c.id == instance_id)

    @asyncio.coroutine
    def get_collection(self, request):
        instances = []
        with (yield from request.app.engine) as conn:
            query = self.get_collection_query(request)
            if self.limit:
                query = query.limit(self.limit)
            result = yield from conn.execute(query)

            if result.returns_rows:
                rows = yield from result.fetchall()
                instances = [dict(zip(row.keys(), row.values()))
                             for row in rows]
        return instances

    @asyncio.coroutine
    def create_instance(self, request, document):
        with (yield from request.app.engine) as conn:
            try:
                query = self.table.insert().values(**document)
                uid = yield from conn.scalar(query)
            except IntegrityError as exc:
                return None, {'IntegrityError': exc.args[0]}
            except ProgrammingError as exc:
                return None, {'ProgrammingError': exc.args[0]}
            else:
                document.update(id=uid)
                return document, {}

    @asyncio.coroutine
    def after_create_instance(self, request, instance):
        pass

    @asyncio.coroutine
    def get_instance(self, request, instance_id):
        instance = None
        with (yield from request.app.engine) as conn:
            query = self.get_instance_query(request, instance_id)
            result = yield from conn.execute(query)

            row = yield from result.fetchone()

            if row:
                instance = dict(zip(row.keys(), row.values()))

        return instance

    @asyncio.coroutine
    def update_instance(self, request, payload, document):
        with (yield from request.app.engine) as conn:
            try:
                query = self.table.update().values(**payload)
                result = yield from conn.execute(query)
            except IntegrityError as exc:
                return None, {'IntegrityError': exc.args[0]}
            except ProgrammingError as exc:
                return None, {'ProgrammingError': exc.args[0]}
            else:
                if result.rowcount:
                    return document, {}
                else:
                    raise web.HTTPNotFound(
                        text='%s not found' % self.resource_name)

    @asyncio.coroutine
    def after_update_instance(self, request, instance, before):
        pass

    @asyncio.coroutine
    def remove_instance(self, request, instance):
        with (yield from request.app.engine) as conn:
            query = self.table.delete().where(self.table.c.id == instance['id'])
            result = yield from conn.execute(query)
        if not result.rowcount:
            raise web.HTTPNotFound(text='%s not found' % self.resource_name)

    @asyncio.coroutine
    def after_remove_instance(self, request, instance):
        pass

    @asyncio.coroutine
    def validate_payload(self, request, payload, instance=None):
        schema = self.schema
        if instance:
            schema = {}
            for key in iter(payload.keys()):
                schema[key] = self.schema[key]

        validator = Validator(schema=schema)
        if instance:
            validator.allow_unknown = True

        if not validator.validate(instance or payload):
            return None, validator.errors

        return validator.document, None

    @asyncio.coroutine
    def get(self, request):
        if 'instance_id' in request.match_info:
            instance_id = request.match_info['instance_id']
            instance = yield from self.get_instance(request, instance_id)

            if instance:
                resource, errors = self.serializer.dump(instance, many=False)
                response = {self.resource_name: resource}
            else:
                raise web.HTTPNotFound(text='%s not found' % self.resource_name)
        else:
            instances = yield from self.get_collection(request)
            collection, errors = self.serializer.dump(instances, many=True)

            response = {
                self.collection_name: collection,
                'meta': {'total': len(collection)}
            }

            if self.limit:
                response['meta']['limit'] = self.limit

        return self.json_response(response)

    @asyncio.coroutine
    def post(self, request):
        payload = yield from self.get_payload(request)

        document, errors = yield from self.validate_payload(request, payload)
        if errors:
            return self.json_response({'errors': errors}, status=400)

        instance, errors = yield from self.create_instance(request, document)
        if errors:
            return self.json_response({'errors': errors}, status=400)

        yield from self.after_create_instance(request, instance)

        response, errors = self.serializer.dump(instance, many=False)
        return self.json_response({self.resource_name: response}, status=201)

    @asyncio.coroutine
    def put(self, request):
        instance_id = request.match_info['instance_id']
        original = yield from self.get_instance(request, instance_id)
        if not original:
            raise web.HTTPNotFound(text='%s not found' % self.resource_name)

        payload = yield from self.get_payload(request)
        instance = original.copy()
        instance.update(**payload)

        document, errors = yield from self.validate_payload(request, payload,
                                                            instance)
        if errors:
            return self.json_response({'errors': errors}, status=400)

        instance, errors = yield from self.update_instance(request, payload,
                                                           document)
        if errors:
            return self.json_response({'errors': errors}, status=400)

        yield from self.after_update_instance(request, instance, original)

        response, errors = self.serializer.dump(instance, many=False)
        return self.json_response({self.resource_name: response})

    @asyncio.coroutine
    def delete(self, request):
        instance_id = request.match_info['instance_id']
        instance = yield from self.get_instance(request, instance_id)
        if not instance:
            raise web.HTTPNotFound(text='%s not found' % self.resource_name)

        yield from self.remove_instance(request, instance)
        yield from self.after_remove_instance(request, instance)

        return web.Response(text='removed')
