from http import HTTPStatus
from typing import Any, Dict, Optional, Tuple, Union

from aiohttp import web
from aiohttp_micro.web.handlers import json_response

from wallet.core.entities import CategoryPayload
from wallet.core.exceptions import CategoryAlreadyExist
from wallet.core.use_cases.categories import AddUseCase, SearchUseCase
from wallet.storage import DBStorage
from wallet.web.handlers.abc import Payload
from wallet.web.handlers.passport import PassportView
from wallet.web.schemas.abc import CommonParameters
from wallet.web.schemas.categories import (
    CategoriesFilterSchema,
    CategoriesResponseSchema,
    CategoryResponseSchema,
    ManageCategoryPayloadSchema,
)


class GetCategoriesView(PassportView):
    """Get categories list"""

    parameters = {
        "common": CommonParameters,
        "filters": CategoriesFilterSchema,
    }

    responses = {
        HTTPStatus.OK: CategoriesResponseSchema,
    }

    async def process_request(
        self, request: web.Request, params: Optional[Dict[str, Any]], **kwargs
    ) -> Union[web.Response, Tuple[Any, HTTPStatus]]:

        search_categories = SearchUseCase(storage=DBStorage(request.app["db"]), logger=request.app["logger"])

        return (
            {"categories": [category async for category in search_categories.execute(filters=params["filters"])]},
            HTTPStatus.OK,
        )


class AddCategoryView(PassportView):
    """Add new category"""

    parameters = {
        "common": CommonParameters,
    }

    payload_cls = ManageCategoryPayloadSchema

    responses = {
        HTTPStatus.CREATED: CategoryResponseSchema,
    }

    async def process_request(
        self, request: web.Request, payload: Optional[Payload] = None, **kwargs
    ) -> Union[web.Response, Tuple[Any, HTTPStatus]]:
        storage = DBStorage(request.app["db"])

        try:
            add_category = AddUseCase(storage=storage, logger=request.app["logger"])
            category = await add_category.execute(payload=CategoryPayload(user=request["user"], name=payload["name"]))

            return {"category": category}, HTTPStatus.CREATED
        except CategoryAlreadyExist:
            return json_response({"errors": {"name": "Already exist"}}, status=422)
