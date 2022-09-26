import ujson
from aiohttp import web


def json_response(data, status: int = 200, **kwargs) -> web.Response:
    """Render response as JSON."""
    return web.Response(body=ujson.dumps(data), status=status, content_type="application/json", **kwargs)
