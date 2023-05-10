from uuid import uuid4

from aiohttp import web
from structlog.contextvars import bind_contextvars, clear_contextvars

from wallet.web import Handler


@web.middleware
async def logging_middleware(
    request: web.Request, handler: Handler
) -> web.StreamResponse:
    """Wrap web-handler with logging.

    Args:
        request: Current request instance.
        handler: Handler for request.
    """
    clear_contextvars()

    context_vars = {
        "request_id": request.headers.get("X-B3-Traceid", str(uuid4().hex)),
        "request_method": request.method,
    }

    if "X-Correlation-ID" in request.headers:
        context_vars["correlation_id"] = request.headers["X-Correlation-ID"]

    bind_contextvars(**context_vars)

    resp = await handler(request)

    bind_contextvars(response_status=resp.status)
    return resp
