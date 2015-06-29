import asyncio

from .base import json_response


@asyncio.coroutine
def index(request):
    return json_response(data={
        'project': request.app.config.get('PROJECT_NAME')
    })