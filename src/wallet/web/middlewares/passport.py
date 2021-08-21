from contextvars import ContextVar

from aiohttp import web
from aiohttp_micro.web.middlewares import Handler
from passport.domain import User
from passport.exceptions import BadToken, TokenExpired
from passport.services.tokens import TokenDecoder


user_context: ContextVar[User] = ContextVar("user", default=None)


@web.middleware
async def middleware(request: web.Request, handler: Handler) -> web.Response:
    token = request.headers.get("X-ACCESS-TOKEN", None)

    if token:
        try:
            config = request.app["config"]
            decoder = TokenDecoder(public_key=config.passport.public_key)
            user: User = decoder.decode(token)
        except (BadToken, TokenExpired):
            raise web.HTTPForbidden

        user_context.set(user)

        request["logger"] = request.app["logger"].bind(user_id=user.key)

    response = await handler(request)

    return response
