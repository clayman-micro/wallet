from aiohttp import web

from . import base


class IndexHandler(base.BaseHandler):
    endpoints = (
        ('GET', '/', 'index'),
    )

    async def get(self, request: web.Request) -> web.Response:
        return self.json_response({
            'project': request.app.config.get('PROJECT_NAME')
        })
