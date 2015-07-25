import asyncio

from . import base


class IndexHandler(base.BaseHandler):
    endpoints = (
        ('GET', '/', 'index'),
    )

    @asyncio.coroutine
    def get(self, request):
        return self.json_response({
            'project': request.app.config.get('PROJECT_NAME')
        })
