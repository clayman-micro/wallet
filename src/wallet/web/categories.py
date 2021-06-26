from typing import Dict

from aiohttp import web
from aiohttp_micro.web.handlers import json_response, validate_payload
from marshmallow import fields, Schema
from passport.client import user_required

from wallet.core.entities import CategoryFilters, CategoryPayload
from wallet.core.exceptions import CategoryAlreadyExist
from wallet.core.use_cases.categories import AddUseCase, SearchUseCase
from wallet.storage import DBStorage
from wallet.web import serialize


class CategorySchema(Schema):
    key = fields.Int(required=True, data_key="id", description="Category id")
    name = fields.Str(required=True, description="Category name")


class CategoriesResponseSchema(Schema):
    categories = fields.List(fields.Nested(CategorySchema), required=True, description="Categories")


@user_required()
@serialize(CategoriesResponseSchema)
async def search(request: web.Request) -> web.Response:
    search_categories = SearchUseCase(storage=DBStorage(request.app["db"]), logger=request.app["logger"])

    return {
        "categories": [
            category async for category in search_categories.execute(filters=CategoryFilters(user=request["user"]))
        ]
    }


class ManageCategoryPayloadSchema(Schema):
    name = fields.Str(required=True, description="Category name")


class CategoryResponseSchema(Schema):
    category = fields.Nested(CategorySchema, required=True)


@user_required()
@validate_payload(ManageCategoryPayloadSchema)
@serialize(CategoryResponseSchema, status=201)
async def add(payload: Dict[str, str], request: web.Request) -> web.Response:
    storage = DBStorage(request.app["db"])

    try:
        add_category = AddUseCase(storage=storage, logger=request.app["logger"])
        category = await add_category.execute(payload=CategoryPayload(user=request["user"], name=payload["name"]))

        return {"category": category}
    except CategoryAlreadyExist:
        return json_response({"errors": {"name": "Already exist"}}, status=422)
