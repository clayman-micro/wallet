from contextvars import ContextVar
from typing import AsyncGenerator, Optional

from aiohttp import ClientSession, web
from aiohttp.typedefs import Handler
from passport.domain import User
from passport.exceptions import BadToken, TokenExpired
from passport.services.tokens import TokenDecoder

user_context: ContextVar[Optional[User]] = ContextVar("user", default=None)


@web.middleware
async def middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    """Passport authentication middleware.

    Args:
        request: Aiohttp web request.
        handler: Web handler function.

    Returns:
        HTTP Response object.
    """
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


async def prepare(app: web.Application) -> AsyncGenerator[None, None]:
    """Prepare application for Passport."""
    config = app["config"]

    app["logger"].debug("Fetch passport keys")

    if not config.passport.host:
        app["logger"].error("Passport host should be defined")
        raise RuntimeError("Passport host should be defined")

    if not config.passport.public_key:
        verify_ssl = True
        if app["config"].debug:
            verify_ssl = False

        url = f"{config.passport.host}/api/keys"

        async with ClientSession() as session:
            async with session.get(url, ssl=verify_ssl) as resp:
                if resp.status != 200:
                    app["logger"].error("Fetch passport keys failed", status=resp.status)
                    raise RuntimeError("Could not fetch passport keys")

                keys = await resp.json()

                config.passport.public_key = keys["public"]

    yield


def setup(app: web.Application) -> None:
    """Setup passport integration.

    Args:
        app: Application instance.
    """
    app.cleanup_ctx.append(prepare)
    app.middlewares.append(middleware)
