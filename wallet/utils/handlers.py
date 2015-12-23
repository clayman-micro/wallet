from contextlib import contextmanager

from aiohttp import web

from ..handlers.base import BaseHandler
from ..exceptions import ImproperlyConfigure


def reverse_url(app: web.Application, name: str, parts=None) -> str:
    return app.router[name].url(parts=parts) if parts \
        else app.router[name].url()


@contextmanager
def register_handler(app: web.Application, url_prefix=None, name_prefix=None):
    def register(method, url, handler, name=None):
        if url_prefix:
            if not url:
                url = url_prefix
            else:
                url = '/'.join((url_prefix.rstrip('/'), url.lstrip('/')))

        if name_prefix:
            name = '.'.join((name_prefix, name))

        if isinstance(handler, BaseHandler):
            endpoint = getattr(handler, method.lower(), None)
            if endpoint:
                if handler.decorators:
                    for decorator in handler.decorators:
                        endpoint = decorator(endpoint)

                app.router.add_route(method, url, endpoint, name=name)
            else:
                raise ImproperlyConfigure(
                    '`%s` handler does not have method `%s`' % (
                        handler, method.lower()
                    ))
        else:
            app.router.add_route(method, url, handler, name=name)
    yield register
