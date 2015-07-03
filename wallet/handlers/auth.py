import asyncio
from datetime import datetime

from aiohttp import web
from cerberus import Validator

from ..models.auth import (users_table, users_schema, encrypt_password,
                           verify_password)
from .base import json_response, get_payload


@asyncio.coroutine
def registration(request):
    payload = yield from get_payload(request)

    validator = Validator(schema=users_schema)
    if not validator.validate(payload):
        return json_response(data=validator.errors, status=400)

    with (yield from request.app.engine) as conn:
        query = users_table.select().where(
            users_table.c.login == payload['login'])
        res = yield from conn.scalar(query)

        if not res:
            query = users_table.insert().values(
                login=payload['login'],
                password=encrypt_password(payload['password']),
                created_on=datetime.now())
            uid = yield from conn.scalar(query)
            return json_response({'id': uid, 'login': payload['login']},
                                 status=201)
        else:
            return json_response({'errors': {
                'login': 'Login already exists'
            }}, status=400)


@asyncio.coroutine
def login(request):
    payload = yield from get_payload(request)

    validator = Validator(schema=users_schema)
    if not validator.validate(payload):
        return json_response(data=validator.errors, status=400)

    with (yield from request.app.engine) as conn:
        query = users_table.select().where(
            users_table.c.login == payload['login'])
        result = yield from conn.execute(query)
        user = yield from result.fetchone()

        if not user:
            raise web.HTTPNotFound(text='User not found.')

        if not verify_password(payload['password'], user.password):
            return json_response({'errors': {
                'password': 'Wrong password'
            }}, status=400)

        token = request.app.signer.dumps({'id': user.id})

        query = users_table.update().where(users_table.c.id == user.id).values(
            last_login=datetime.now())
        yield from conn.execute(query)

        return json_response({'user': {'id': user.id}}, headers={
            'X-ACCESS-TOKEN': token.decode('utf-8')
        })
