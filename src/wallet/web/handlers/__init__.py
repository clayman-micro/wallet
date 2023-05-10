from typing import Any

import ujson
from aiohttp import web


def json_response(
    data: dict[str, Any], status: int = 200, **kwargs: Any
) -> web.Response:
    """Render response as JSON."""
    return web.Response(
        body=ujson.dumps(data),
        status=status,
        content_type="application/json",
        **kwargs,
    )
