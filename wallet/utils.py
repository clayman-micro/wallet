from contextlib import contextmanager

from aiohttp import web


class Connection(object):

    def __init__(self, engine):
        self.conn = None
        self.engine = engine

    async def __aenter__(self):
        self.conn = await self.engine.acquire()
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        try:
            self.engine.release(self.conn)
        finally:
            self.conn = None
            self.engine = None


def reverse_url(app: web.Application, name: str, parts=None) -> str:
    return app.router[name].url(parts=parts) if parts \
        else app.router[name].url()


@contextmanager
def register_handler(app: web.Application, url_prefix=None, name_prefix=None):
    def register(method, url, handler, name=None):
        if url_prefix:
            url = '/'.join((url_prefix.rstrip('/'), url.lstrip('/')))

        if name_prefix:
            name = '.'.join((name_prefix, name))

        app.router.add_route(method, url, handler, name=name)
    yield register
