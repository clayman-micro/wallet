from aiohttp import web

from wallet.adapters.web import get_payload, json_response
from wallet.adapters.web.users import user_required
from wallet.services.accounts import AccountsService, AccountValidator
from wallet.storage import DBStorage


@user_required
async def register(request: web.Request) -> web.Response:
    payload = await get_payload(request)

    validator = AccountValidator()
    document = validator.validate_payload(payload)

    async with request.app['db'].acquire() as conn:
        storage = DBStorage(conn)

        service = AccountsService(storage)
        account = await service.register(name=document['name'], user=request['user'])

    return json_response({
        'account': {
            'id': account.key,
            'name': account.name,
        }
    }, status=201)
