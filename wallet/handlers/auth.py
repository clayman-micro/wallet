import asyncio
from datetime import datetime
from functools import wraps

from aiohttp import web
from cerberus import Validator
import itsdangerous

from ..models import auth
from . import base


def owner_required(f):
    @asyncio.coroutine
    @wraps(f)
    def wrapped(*args):
        if asyncio.iscoroutinefunction(f):
            coro = f
        else:
            coro = asyncio.coroutine(f)
        request = args[-1]

        token = request.headers.get('X-ACCESS-TOKEN', None)
        if token:
            try:
                data = request.app.signer.loads(token)
            except itsdangerous.SignatureExpired:
                raise web.HTTPUnauthorized(text='Token signature expired')
            except itsdangerous.BadSignature:
                raise web.HTTPUnauthorized(text='Bad token signature')
            else:
                user_id = data.get('id')
                with (yield from request.app.engine) as conn:
                    query = auth.users_table.select().where(
                        auth.users_table.c.id == user_id)
                    result = yield from conn.execute(query)
                    row = yield from result.fetchone()

                if row:
                    request.owner = dict(zip(row.keys(), row.values()))
                    return (yield from coro(*args))
                else:
                    raise web.HTTPNotFound(text='owner not found')
        else:
            raise web.HTTPUnauthorized(text='Access token required')
    return wrapped


class RegistrationHandler(base.BaseHandler):
    endpoints = (
        ('POST', '/register', 'registration'),
    )

    @asyncio.coroutine
    def post(self, request):
        payload = yield from self.get_payload(request)

        validator = Validator(schema=auth.users_schema)
        if not validator.validate(payload):
            return self.json_response(validator.errors, status=400)

        with (yield from request.app.engine) as conn:
            query = auth.users_table.select().where(
                auth.users_table.c.login == payload['login'])
            res = yield from conn.scalar(query)

            if not res:
                query = auth.users_table.insert().values(
                    login=payload['login'],
                    password=auth.encrypt_password(payload['password']),
                    created_on=datetime.now())
                uid = yield from conn.scalar(query)
                return self.json_response(
                    {'id': uid, 'login': payload['login']}, status=201)
            else:
                return self.json_response({'errors': {
                    'login': 'Login already exists'
                }}, status=400)


class LoginHandler(base.BaseHandler):
    endpoints = (
        ('POST', '/login', 'login'),
    )

    @asyncio.coroutine
    def post(self, request):
        payload = yield from self.get_payload(request)

        validator = Validator(schema=auth.users_schema)
        if not validator.validate(payload):
            return self.json_response(validator.errors, status=400)

        with (yield from request.app.engine) as conn:
            query = auth.users_table.select().where(
                auth.users_table.c.login == payload['login'])
            result = yield from conn.execute(query)
            user = yield from result.fetchone()

            if not user:
                raise web.HTTPNotFound(text='User not found.')

            if not auth.verify_password(payload['password'], user.password):
                return self.json_response({'errors': {
                    'password': 'Wrong password'
                }}, status=400)

            token = request.app.signer.dumps({'id': user.id})

            query = auth.users_table.update().where(
                auth.users_table.c.id == user.id).values(
                last_login=datetime.now())
            yield from conn.execute(query)

            return self.json_response({'user': {'id': user.id}}, headers={
                'X-ACCESS-TOKEN': token.decode('utf-8')
            })
