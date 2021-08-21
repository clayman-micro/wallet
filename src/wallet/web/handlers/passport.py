from typing import Type

from aiohttp import web
from marshmallow import Schema

from wallet.web.handlers.abc import OperationView
from wallet.web.middlewares.passport import user_context


class PassportView(OperationView):
    """Basic view with required authorized user"""

    def create_schema(self, schema_cls: Type[Schema]) -> Schema:
        schema = super().create_schema(schema_cls)
        schema.context["user"] = user_context.get()
        return schema

    async def handle(self, request: web.Request) -> web.Response:
        user = user_context.get()

        if not user:
            raise web.HTTPUnauthorized(text="Authorization required")

        return await super().handle(request)
