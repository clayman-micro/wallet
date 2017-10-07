import pytest

from tests.handlers import prepare_request

from wallet.storage.accounts import AccountsRepo


@pytest.mark.handlers
@pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
@pytest.mark.parametrize('method,endpoint,parts', (
    ('GET', 'api.accounts.get_accounts', None),
    ('POST', 'api.accounts.create_account', None),
    ('GET', 'api.accounts.get_account', {'instance_id': 1}),
    ('PUT', 'api.accounts.update_account', {'instance_id': 1}),
    ('DELETE', 'api.accounts.remove_account', {'instance_id': 1}),
))
async def test_unauthorized(client, passport, headers, method, endpoint, parts):
    app: App = client.server.app
    app.config['passport_dsn'] = passport

    if parts:
        url = app.router.named_resources()[endpoint].url(parts=parts)
    else:
        url = app.router.named_resources()[endpoint].url()

    call_method = getattr(client, method.lower())
    resp = await call_method(url, headers=headers)

    assert resp.status == 401


@pytest.mark.handlers
async def test_get_accounts(client, passport, owner):
    app = client.server.app
    app.config['passport_dsn'] = passport

    async with app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        await repo.create('Foo', owner)

    url = app.router.named_resources()['api.accounts.get_accounts'].url()
    resp = await client.get(url, headers={'X-ACCESS-TOKEN': owner.token})

    assert resp.status == 200
    result = await resp.json()
    assert result['accounts'] == [{
        'id': 1, 'name': 'Foo', 'amount': 0.0, 'original': 0.0
    }]


@pytest.mark.handlers
async def test_get_accounts_with_filter(client, passport, owner):
    app = client.server.app
    app.config['passport_dsn'] = passport

    async with app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        for name in ('Foo', 'Bar', 'Baz'):
            await repo.create(name, owner)

    url = app.router.named_resources()['api.accounts.get_accounts'].url()
    resp = await client.get(f'{url}?name=F',
                            headers={'X-ACCESS-TOKEN': owner.token})

    assert resp.status == 200
    result = await resp.json()
    assert result['accounts'] == [{
        'id': 1, 'name': 'Foo', 'amount': 0.0, 'original': 0.0
    }]
    assert result['meta'] == {'total': 1, 'search': {'name': 'F'}}


@pytest.mark.handlers
@pytest.mark.parametrize('json', (True, False))
async def test_create_success(client, passport, owner, json):
    app = client.server.app
    app.config['passport_dsn'] = passport

    data = {'name': 'Foo'}

    url = app.router.named_resources()['api.accounts.create_account'].url()
    resp = await client.post(url, **prepare_request(
        data, {'X-ACCESS-TOKEN': owner.token}, json
    ))

    assert resp.status == 201
    result = await resp.json()
    assert result['account'] == {
        'id': 1, 'name': 'Foo', 'amount': 0.0, 'original': 0.0
    }


@pytest.mark.handlers
@pytest.mark.parametrize('json', (True, False))
async def test_create_with_name_conflict(client, passport, owner, json):
    app = client.server.app
    app.config['passport_dsn'] = passport

    async with app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        await repo.create('Foo', owner)

    data = {'name': 'Foo'}

    url = app.router.named_resources()['api.accounts.create_account'].url()
    resp = await client.post(url, **prepare_request(
        data, {'X-ACCESS-TOKEN': owner.token}, json
    ))

    assert resp.status == 400


@pytest.mark.handlers
@pytest.mark.parametrize('method, endpoint', (
    ('GET', 'api.accounts.get_account'),
    ('PUT', 'api.accounts.update_account'),
    ('DELETE', 'api.accounts.remove_account'),
))
async def test_missing(client, passport, owner, method, endpoint):
    app = client.server.app
    app.config['passport_dsn'] = passport

    url = app.router.named_resources()[endpoint].url(parts={
        'instance_id': 1
    })
    call_method = getattr(client, method.lower())
    resp = await call_method(url, headers={'X-ACCESS-TOKEN': owner.token})

    assert resp.status == 404


@pytest.mark.handlers
async def test_get_account(client, passport, owner):
    app = client.server.app

    async with app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        for name in ('Foo', 'Bar', 'Baz'):
            await repo.create(name, owner)

    url = app.router.named_resources()['api.accounts.get_account'].url(
        parts={'instance_id': 1})
    resp = await client.get(url, headers={'X-ACCESS-TOKEN': owner.token})

    assert resp.status == 200
    result = await resp.json()
    assert result['account'] == {
        'id': 1, 'name': 'Foo', 'amount': 0.0, 'original': 0.0
    }


@pytest.mark.handlers
async def test_remove(client, passport, owner):
    app = client.server.app
    app.config['passport_dsn'] = passport

    async with app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        for name in ('Foo', 'Bar', 'Baz'):
            await repo.create(name, owner)

    url = app.router.named_resources()['api.accounts.get_account'].url(
        parts={'instance_id': 1})
    resp = await client.delete(url, headers={'X-ACCESS-TOKEN': owner.token})

    assert resp.status == 200
