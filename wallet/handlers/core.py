from aiohttp import web

from .base import handle_response


@handle_response
async def index(request: web.Request) -> web.Response:
    return {
        'project': request.app['config'].get('PROJECT_NAME')
    }
