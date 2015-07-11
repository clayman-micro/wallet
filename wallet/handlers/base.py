import asyncio
from psycopg2 import ProgrammingError, IntegrityError
from aiohttp import web
from functools import wraps
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


def get_collection(table, serializer, collection_name, limit=10):
    @asyncio.coroutine
    def wrapper(*args, **kwargs):
        request = args[0]

        response_content = []
        total = 0
        with (yield from request.app.engine) as conn:
            query = table.select().limit(limit)
            result = yield from conn.execute(query)

            if result.returns_rows:
                instances = yield from result.fetchall()

                response_content, errors = serializer.dump(instances,
                                                           many=True)
                total = len(response_content)
        response = {
            collection_name: response_content,
            'meta': {
                'total': total,
                'limit': limit,
                'collection_url': reverse_url(request, 'api.get_%s' % collection_name)
            }
        }

        return json_response(response)
    return wrapper


def get_resource(table, serializer, resource_name):
    @asyncio.coroutine
    def wrapper(*args, **kwargs):
        request = args[0]
        instance_id = request.match_info['instance_id']

        with (yield from request.app.engine) as conn:
            query = table.select().where(table.c.id == instance_id)
            result = yield from conn.execute(query)

            instance = yield from result.fetchone()

            if instance:
                response_content, errors = serializer.dump(instance, many=False)

                return json_response({
                    resource_name: response_content,
                })
            else:
                raise web.HTTPNotFound(text='%s not found' % resource_name)
    return wrapper


def create_resource(table, serializer, resource_name):
    def decorator(f):
        @wraps(f)
        @asyncio.coroutine
        def wrapper(*args, **kwargs):
            request = args[0]

            payload = yield from get_payload(request)
            kwargs.update(payload=payload)

            document, errors = yield from f(*args, **kwargs)

            if errors:
                return json_response({
                    'errors': errors
                }, status=400)

            with (yield from request.app.engine) as conn:
                try:
                    query = table.insert().values(**document)
                    uid = yield from conn.scalar(query)
                except IntegrityError as exc:
                    return json_response({
                        'errors': {
                            'IntegrityError': exc.args[0]
                        },
                    }, status=400)
                except ProgrammingError as exc:
                    return json_response({
                        'errors': {
                            'ProgrammingError': exc.args[0]
                        }
                    })
                else:
                    document.update(id=uid)

            response, errors = serializer.dump(document, many=False)
            return json_response({
                resource_name: response
            }, status=201)
        return wrapper
    return decorator


def update_resource(table, serializer, resource_name):
    def decorator(f):
        @wraps(f)
        @asyncio.coroutine
        def wrapper(*args, **kwargs):
            request = args[0]

            instance_id = request.match_info['instance_id']

            with (yield from request.app.engine) as conn:
                query = table.select().where(table.c.id == instance_id)
                result = yield from conn.execute(query)

                row = yield from result.fetchone()

            if not row:
                raise web.HTTPNotFound(text='%s not found' % resource_name)

            instance = dict(zip(row.keys(), row.values()))

            payload = yield from get_payload(request)
            instance.update(**payload)
            kwargs.update(payload=payload, instance=instance)

            document, errors = yield from f(*args, **kwargs)

            if errors:
                return json_response({
                    'errors': errors
                }, status=400)

            with (yield from request.app.engine) as conn:
                try:
                    query = table.update().where(
                        table.c.id == instance_id).values(**payload)
                    result = yield from conn.execute(query)
                except IntegrityError as exc:
                    return json_response({
                        'errors': {
                            'IntegrityError': exc.args[0]
                        },
                    }, status=400)
                except ProgrammingError as exc:
                    return json_response({
                        'errors': {
                            'ProgrammingError': exc.args[0]
                        }
                    })

                if result.rowcount:
                    response, errors = serializer.dump(document, many=False)
                    return json_response({
                        resource_name: response
                    })
                else:
                    raise web.HTTPNotFound(text='%s not found' % resource_name)
        return wrapper
    return decorator


def delete_resource(table, resource_name):
    @asyncio.coroutine
    def wrapper(*args, **kwargs):
        request = args[0]

        instance_id = request.match_info['instance_id']

        with (yield from request.app.engine) as conn:
            query = table.delete().where(table.c.id == instance_id)
            result = yield from conn.execute(query)

        if result.rowcount:
            return web.Response(text='removed')
        else:
            raise web.HTTPNotFound(text='%s not found' % resource_name)
    return wrapper
