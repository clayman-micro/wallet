from functools import wraps

import ujson  # type: ignore
from aiohttp import ClientSession, web

from wallet.adapters.web import Handler
from wallet.domain.entities import User, UserProvider


class BadToken(Exception):
    pass


class BrokenPassportResponse(Exception):
    pass


class PassportProvider(UserProvider):
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    async def identify(self, token: str) -> User:
        headers = {'X-ACCESS-TOKEN': token}
        url = f'{self._dsn}/api/identify'

        async with ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                status = resp.status
                text = await resp.text()

        if status == 200:
            try:
                data = ujson.loads(text)
            except KeyError:
                raise BrokenPassportResponse()
            else:
                user = User(data['owner']['id'], data['owner']['email'])
        elif status == 401:
            raise BadToken()
        else:
            raise BrokenPassportResponse()

        return user


def user_required(f):
    @wraps(f)
    async def wrapped(request: web.Request) -> web.Response:
        if 'user' in request and isinstance(request['user'], User):
            return await f(request)
        else:
            raise web.HTTPUnauthorized

    return wrapped


@web.middleware
async def auth_middleware(request: web.Request, handler: Handler) -> web.Response:
    token = request.headers.get('X-Access-Token', None)
    if token:
        try:
            user = await request.app['passport'].identify(token)
            request['user'] = user
        except BadToken:
            raise web.HTTPUnauthorized

    response = await handler(request)
    return response
