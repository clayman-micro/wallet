from aiohttp import web

from wallet.handlers import (get_instance_id, get_payload, json_response,
                             register_handler)
from wallet.storage import AlreadyExist
from wallet.storage.accounts import AccountsRepo
from wallet.storage.owner import Owner
from wallet.validation import to_decimal, ValidationError, Validator


schema = {
    'id': {
        'type': 'integer',
    },
    'name': {
        'type': 'string', 'maxlength': 255, 'required': True, 'empty': False
    },
    'amount': {
        'type': 'decimal', 'coerce': to_decimal(2), 'empty': True
    },
    'original': {
        'type': 'decimal', 'coerce': to_decimal(2), 'empty': True
    },
    'created_on': {
        'type': 'datetime', 'empty': True
    },
    'owner_id': {
        'type': 'integer', 'coerce': int, 'readonly': True
    }
}


async def get_accounts(owner: Owner, request: web.Request) -> web.Response:
    name = None
    if 'name' in request.query and request.query['name']:
        name = request.query['name']

    async with request.app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        accounts = await repo.fetch_many(owner, name=name)

    meta = {'total': len(accounts)}
    if name:
        meta['search'] = {'name': name}

    accounts = list(map(lambda item: item.serialize(), accounts))
    return json_response({'accounts': accounts, 'meta': meta})


async def create_account(owner: Owner, request: web.Request) -> web.Response:
    payload = await get_payload(request)

    validator = Validator(schema)
    document = validator.validate_payload(payload)

    async with request.app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        try:
            account = await repo.create(document['name'], owner,
                                        amount=document.get('amount', 0.0),
                                        original=document.get('original', 0.0))
        except AlreadyExist:
            raise ValidationError({'name': 'Already exist'})

    return json_response({'account': account.serialize()}, status=201)


async def get_account(owner: Owner, request: web.Request) -> web.Response:
    account_id = get_instance_id(request)

    async with request.app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        account = await repo.fetch(owner, account_id)

    return json_response({'account': account.serialize()})


async def update_account(owner: Owner, request: web.Request) -> web.Response:
    account_id = get_instance_id(request)

    payload = await get_payload(request)

    async with request.app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        account = await repo.fetch(owner, account_id)

        validator = Validator(schema)
        document = validator.validate_payload(payload)

        success = await repo.rename(account, document['name'])

        if success:
            account.name = document['name']

    return json_response({'account': account.serialize()})


async def remove_account(owner: Owner, request: web.Request) -> web.Response:
    tag_id = get_instance_id(request)

    async with request.app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        account = await repo.fetch(owner, tag_id)
        removed = await repo.remove(account)

    return web.Response(status=200 if removed else 400)


def register(app, url_prefix, name_prefix):
    with register_handler(app, url_prefix, name_prefix) as register:
        register('GET', '', get_accounts, 'get_accounts')
        register('POST', '', create_account, 'create_account')
        register('GET', '{instance_id}', get_account, 'get_account')
        register('PUT', '{instance_id}', update_account, 'update_account')
        register('DELETE', '{instance_id}', remove_account, 'remove_account')
