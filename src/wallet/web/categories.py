from http import HTTPStatus
from typing import Dict

from aiohttp import web
from aiohttp_micro.web.handlers import json_response
from aiohttp_micro.web.handlers.openapi import OpenAPISpec, PayloadSchema, ResponseSchema
from marshmallow import fields, Schema
from passport.client import user_required

from wallet.core.entities import CategoryFilters, CategoryPayload
from wallet.core.exceptions import CategoryAlreadyExist
from wallet.core.use_cases.categories import AddUseCase, SearchUseCase
from wallet.storage import DBStorage
from wallet.web import CollectionFiltersSchema, CommonParameters, serialize, validate_payload


class CategorySchema(Schema):
    key = fields.Int(required=True, data_key="id", description="Category id")
    name = fields.Str(required=True, description="Category name")


class CategoriesResponseSchema(ResponseSchema):
    """Categories list."""

    categories = fields.List(fields.Nested(CategorySchema), required=True, description="Categories")


class CategoriesFilterSchema(CollectionFiltersSchema):
    """Filter categories list."""


@user_required()
@serialize(CategoriesResponseSchema)
async def search(request: web.Request) -> web.Response:
    """Get categories list."""

    search_categories = SearchUseCase(storage=DBStorage(request.app["db"]), logger=request.app["logger"])

    return {
        "categories": [
            category async for category in search_categories.execute(filters=CategoryFilters(user=request["user"]))
        ]
    }


search.spec = OpenAPISpec(
    operation="getCategories",
    parameters=[CommonParameters, CategoriesFilterSchema],
    responses={
        HTTPStatus.OK: CategoriesResponseSchema,
        # HTTPStatus.UNAUTHORIZED: ErrorSchema,
        # HTTPStatus.FORBIDDEN: ErrorSchema,
    },
    security="TokenAuth",
    tags=["categories"],
)


class ManageCategoryPayloadSchema(PayloadSchema):
    """Add new category."""

    name = fields.Str(required=True, description="Category name")


class CategoryResponseSchema(ResponseSchema):
    """Get category info."""

    category = fields.Nested(CategorySchema, required=True)


@user_required()
@validate_payload(ManageCategoryPayloadSchema)
@serialize(CategoryResponseSchema, status=201)
async def add(payload: Dict[str, str], request: web.Request) -> web.Response:
    """Add new category."""

    storage = DBStorage(request.app["db"])

    try:
        add_category = AddUseCase(storage=storage, logger=request.app["logger"])
        category = await add_category.execute(payload=CategoryPayload(user=request["user"], name=payload["name"]))

        return {"category": category}
    except CategoryAlreadyExist:
        return json_response({"errors": {"name": "Already exist"}}, status=422)


add.spec = OpenAPISpec(
    operation="addCategory",
    parameters=[CommonParameters],
    payload=ManageCategoryPayloadSchema,
    responses={
        HTTPStatus.OK: CategoryResponseSchema,
        # HTTPStatus.UNAUTHORIZED: ErrorSchema,
        # HTTPStatus.FORBIDDEN: ErrorSchema,
    },
    security="TokenAuth",
    tags=["categories"],
)
