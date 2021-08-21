from http import HTTPStatus
from typing import Any, Dict, Optional, Tuple, Union

from aiohttp import web

from wallet.core.use_cases.operations import AddUseCase, SearchUseCase
from wallet.storage import DBStorage
from wallet.web.handlers.abc import Payload
from wallet.web.handlers.passport import PassportView
from wallet.web.schemas.abc import CommonParameters
from wallet.web.schemas.operations import (
    AddOperationPayloadSchema,
    ErrorsResponseSchema,
    OperationResponseSchema,
    OperationsFilterSchema,
    OperationsResponseSchema,
)


class GetOperationsView(PassportView):
    """Get operations list"""

    parameters = {
        "common": CommonParameters,
        "filters": OperationsFilterSchema,
    }

    responses = {
        HTTPStatus.OK: OperationsResponseSchema,
        HTTPStatus.BAD_REQUEST: ErrorsResponseSchema,
    }

    async def process_request(
        self, request: web.Request, params: Optional[Dict[str, Any]], **kwargs
    ) -> Union[web.Response, Tuple[Any, HTTPStatus]]:
        search_operations = SearchUseCase(storage=DBStorage(request.app["db"]), logger=request.app["logger"])
        return (
            {
                "operations": [operation async for operation in search_operations.execute(filters=params["filters"])],
                "meta": {"filters": params["filters"]},
            },
            HTTPStatus.OK,
        )


class AddOperationView(PassportView):
    """Add new operation"""

    parameters = {"common": CommonParameters}

    payload_cls = AddOperationPayloadSchema

    responses = {
        HTTPStatus.CREATED: OperationResponseSchema,
        # HTTPStatus.UNAUTHORIZED: ErrorSchema,
        # HTTPStatus.FORBIDDEN: ErrorSchema,
    }

    async def process_request(
        self, request: web.Request, payload: Optional[Payload] = None, **kwargs
    ) -> Union[web.Response, Tuple[Any, HTTPStatus]]:
        add_operation = AddUseCase(storage=DBStorage(request.app["db"]), logger=request.app["logger"])
        operation = await add_operation.execute(payload=payload)

        return {"operation": operation}, HTTPStatus.CREATED
