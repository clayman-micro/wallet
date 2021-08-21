from aiohttp_micro.web.handlers.openapi import PayloadSchema, ResponseSchema
from marshmallow import fields, post_load, Schema

from wallet.core.entities.categories import CategoryFilters
from wallet.web.schemas.abc import CollectionFiltersSchema


class CategorySchema(Schema):
    key = fields.Int(required=True, data_key="id", description="Category id")
    name = fields.Str(required=True, description="Category name")


class CategoriesResponseSchema(ResponseSchema):
    """Categories list."""

    categories = fields.List(fields.Nested(CategorySchema), required=True, description="Categories")


class CategoriesFilterSchema(CollectionFiltersSchema):
    """Filter categories list."""

    @post_load
    def make_payload(self, data, **kwargs):
        return CategoryFilters(user=self.context["user"])


class ManageCategoryPayloadSchema(PayloadSchema):
    """Add new category."""

    name = fields.Str(required=True, description="Category name")


class CategoryResponseSchema(ResponseSchema):
    """Get category info."""

    category = fields.Nested(CategorySchema, required=True)
