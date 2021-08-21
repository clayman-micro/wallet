from http import HTTPStatus
from typing import Any, Dict, Optional, Tuple, Union

from aiohttp import web
from aiohttp_micro.web.handlers import json_response

from wallet.core.exceptions import AccountAlreadyExist
from wallet.core.use_cases.accounts import AddUseCase, SearchUseCase
from wallet.storage import DBStorage
from wallet.web.handlers.abc import Payload
from wallet.web.handlers.passport import PassportView
from wallet.web.schemas.abc import CommonParameters
from wallet.web.schemas.accounts import (
    AccountResponseSchema,
    AccountsFilterSchema,
    AccountsResponseSchema,
    ManageAccountPayloadSchema,
)


class GetAccountsView(PassportView):
    """Get accounts list"""

    parameters = {"common": CommonParameters, "filters": AccountsFilterSchema}

    responses = {
        HTTPStatus.OK: AccountsResponseSchema,
        # HTTPStatus.BAD_REQUEST: ErrorsResponseSchema,
    }

    async def process_request(
        self, request: web.Request, params: Optional[Dict[str, Any]], **kwargs
    ) -> Union[web.Response, Tuple[Any, HTTPStatus]]:

        search_accounts = SearchUseCase(DBStorage(request.app["db"]), logger=request.app["logger"])

        return (
            {"accounts": [account async for account in search_accounts.execute(filters=params["filters"])]},
            HTTPStatus.OK,
        )


class AddAccountView(PassportView):
    """Add new account"""

    parameters = {"common": CommonParameters}

    payload_cls = ManageAccountPayloadSchema

    responses = {
        HTTPStatus.CREATED: AccountResponseSchema,
    }

    async def process_request(
        self, request: web.Request, payload: Optional[Payload] = None, **kwargs
    ) -> Union[web.Response, Tuple[Any, HTTPStatus]]:
        storage = DBStorage(request.app["db"])

        try:
            add_account = AddUseCase(storage, logger=request.app["logger"])
            account = await add_account.execute(payload=payload)

            return {"account": account}, HTTPStatus.CREATED
        except AccountAlreadyExist:
            return json_response({"errors": {"name": "Already exist"}}, status=422)
