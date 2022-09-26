from aiohttp import web

from wallet.web import json_response


async def index(request: web.Request) -> web.Response:
    """Get app meta information."""
    return json_response(
        {
            "hostname": request.app["hostname"],
            "project": request.app["distribution"].project_name,
            "version": request.app["distribution"].version,
        }
    )


async def health(request: web.Request) -> web.Response:
    """Health check."""
    return web.Response(body=b"Healthy")
