from datetime import datetime, timedelta
from functools import wraps
from typing import Dict

from aiohttp import web
from cerberus import Validator
import jwt
from sqlalchemy import select, func

from wallet.utils.handlers import register_handler
from ..exceptions import ValidationError
from ..storage import users
from . import base


def owner_required(f):
    @wraps(f)
    async def wrapped(*args, **kwargs):
        request = args[0]

        token = request.headers.get('X-ACCESS-TOKEN', None)

        if not token:
            raise web.HTTPUnauthorized(text='Access token required')

        try:
            data = jwt.decode(token, request.app['config'].get('SECRET_KEY'),
                              algorithm='HS256')
        except jwt.ExpiredSignatureError:
            raise web.HTTPUnauthorized(text='Token signature expired')
        except jwt.DecodeError:
            raise web.HTTPUnauthorized(text='Bad token signature')
        else:
            user_id = data.get('id')
            async with request.app['engine'].acquire() as conn:
                query = select([users.table]).where(users.table.c.id == user_id)
                result = await conn.execute(query)
                row = await result.fetchone()

            if row:
                owner = dict(zip(row.keys(), row.values()))
                kwargs['owner'] = owner
                return await f(*args, **kwargs)
            else:
                raise web.HTTPNotFound(text='owner not found')
    return wrapped


@base.handle_response
async def register(request: web.Request) -> Dict:
    payload = await base.get_payload(request)

    validator = Validator(schema=users.schema)
    if not validator.validate(payload):
        raise ValidationError(validator.errors)

    uid = 0
    query = select([func.count()]).select_from(users.table).where(
        users.table.c.login == payload['login']
    )
    async with request.app['engine'].acquire() as conn:
        count = await conn.scalar(query)

        if count:
            raise ValidationError({'login': 'Already exists'})

        query = users.table.insert().values(
            login=payload['login'],
            password=users.encrypt_password(payload['password']),
            created_on=datetime.now()
        )
        uid = await conn.scalar(query)

    return base.json_response({
        'id': uid,
        'login': payload['login']
    }, status=201)


@base.handle_response
async def login(request: web.Request) -> Dict:
    payload = await base.get_payload(request)

    validator = Validator(schema=users.schema)
    if not validator.validate(payload):
        raise ValidationError(validator.errors)

    query = select([users.table]).where(users.table.c.login == payload['login'])
    async with request.app['engine'].acquire() as conn:
        result = await conn.execute(query)

        user = await result.fetchone()
        if not user:
            raise web.HTTPNotFound(text='User not found.')

        if not users.verify_password(payload['password'], user.password):
            raise ValidationError({'password': 'Wrong password'})

        query = users.table.update().where(
            users.table.c.id == user.id).values(
            last_login=datetime.now())
        await conn.execute(query)

    config = request.app['config']
    expire = datetime.now() + timedelta(
        seconds=config.get('TOKEN_EXPIRES'))

    token = jwt.encode({
        'id': user.id,
        'exp': expire
    }, config.get('SECRET_KEY'), algorithm='HS256')

    return base.json_response({'user': {
        'id': user.id,
        'login': user.login
    }}, headers={
        'X-ACCESS-TOKEN': token.decode('utf-8'),
        'X-ACCESS-TOKEN-EXPIRE': str(int(expire.timestamp() * 1000))
    })


def register(app):
    with register_handler(app, '/auth', 'auth') as register:
        register('POST', 'login', login, 'login')
        register('POST', 'register', register, 'registration')
