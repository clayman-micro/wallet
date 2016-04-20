import pytest

from wallet.storage import accounts

from . import create_account


@pytest.mark.run_loop
@pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
@pytest.mark.parametrize('method, endpoint, endpoint_params', [
    ('GET', 'api.get_accounts', None),
    ('POST', 'api.create_account', None),
    ('GET', 'api.get_account', {'instance_id': 1}),
    ('PUT', 'api.update_account', {'instance_id': 1}),
    ('DELETE', 'api.remove_account', {'instance_id': 1})
])
async def test_unauthorized(client, headers, method, endpoint, endpoint_params):
    params = {'headers': headers, 'endpoint': endpoint,
              'endpoint_params': endpoint_params}
    async with client.request(method, **params) as response:
        assert response.status == 401


@pytest.mark.run_loop
async def test_collection(app, client, owner):
    account = await create_account({
        'name': 'Credit card', 'original_amount': 3000.0,
        'owner_id': owner['id']
    }, app=app)

    params = await client.get_params('api.get_accounts', owner['credentials'])
    async with client.request('GET', **params) as response:
        assert response.status == 200

        data = await response.json()
        assert 'accounts' in data
        assert data['accounts'] == [{
            'id': account['id'], 'name': 'Credit card',
            'balance': {'expense': 0.0, 'income': 0.0, 'remain': 3000.0}
        }, ]


@pytest.mark.run_loop
async def test_collection_only_for_owner(app, client, owner, stranger):
    await create_account({
        'name': 'Credit card', 'original_amount': 3000.0,
        'owner_id': owner['id']
    }, app=app)

    params = await client.get_params('api.get_accounts', stranger['credentials'])
    async with client.request('GET', **params) as response:
        assert response.status == 200
        result = await response.json()
        assert 'accounts' in result
        assert len(result['accounts']) == 0


@pytest.mark.run_loop
@pytest.mark.parametrize('json', (True, False))
async def test_create(client, owner, json):
    params = await client.get_params('api.create_account', owner['credentials'])
    params.update(data={'name': 'Credit card', 'original_amount': 300.0},
                  json=json)

    async with client.request('POST', **params) as response:
        assert response.status == 201
        result = await response.json()
        assert 'account' in result
        assert result['account'] == {
            'id': 1,
            'name': 'Credit card',
            'balance': {'remain': 300.0, 'income': 0.0, 'expense': 0.0}
        }


@pytest.mark.run_loop
@pytest.mark.parametrize('json', (True, False))
async def test_create_with_name_conflict(app, client, owner, json):
    await create_account({'name': 'Test', 'original_amount': 0.0,
                          'owner_id': owner['id']}, app)

    params = await client.get_params('api.create_account', owner['credentials'])
    params.update(data={'name': 'Test'}, json=json)

    async with client.request('POST', **params) as response:
        assert response.status == 400
        result = await response.json()
        assert 'errors' in result
        assert 'name' in result['errors']


@pytest.mark.run_loop
@pytest.mark.parametrize('method, endpoint', (
    ('GET', 'api.get_account'),
    ('PUT', 'api.update_account'),
    ('DELETE', 'api.remove_account')
))
async def test_missing(client, owner, method, endpoint):
    params = await client.get_params(endpoint, owner['credentials'], 1)
    async with client.request(method, **params) as response:
        assert response.status == 404


@pytest.mark.run_loop
@pytest.mark.parametrize('method, endpoint', (
    ('GET', 'api.get_account'),
    ('PUT', 'api.update_account'),
    ('DELETE', 'api.remove_account')
))
async def test_access_for_strangers(client, stranger, account, method,
                                    endpoint):

    params = await client.get_params(endpoint, stranger['credentials'],
                                     account['id'])
    async with client.request(method, **params) as response:
        assert response.status == 404


@pytest.mark.run_loop
async def test_get_resource(app, client, owner):
    account = await create_account({'name': 'Card', 'original_amount': 390.0,
                                    'owner_id': owner['id']}, app)

    params = await client.get_params('api.get_account', owner['credentials'],
                                     account['id'])
    async with client.request('GET', **params) as response:
        assert response.status == 200

        data = await response.json()
        assert 'account' in data
        assert data['account'] == {
            'id': 1, 'name': 'Card', 'balance': {
                'remain': 390.0, 'income': 0.0, 'expense': 0.0
            }
        }


@pytest.mark.run_loop
@pytest.mark.parametrize('json', (True, False))
async def test_update_resource(app, client, owner, json):
    account = await create_account({'name': 'Card', 'original_amount': 390.0,
                                    'owner_id': owner['id']}, app)

    params = await client.get_params('api.update_account', owner['credentials'],
                                     account['id'])
    params.update(data={'name': 'Deposit'}, json=json)
    async with client.request('PUT', **params) as response:
        assert response.status == 200

        data = await response.json()
        assert 'account' in data
        assert data['account'] == {
            'id': 1, 'name': 'Deposit', 'balance': {
                'remain': 390.0, 'income': 0.0, 'expense': 0.0
            }
        }


@pytest.mark.run_loop
async def test_remove_resource(app, client, owner):
    account = await create_account({'name': 'Card', 'original_amount': 390.0,
                                    'owner_id': owner['id']}, app)

    params = await client.get_params('api.remove_account', owner['credentials'],
                                     account['id'])
    async with client.request('DELETE', **params) as response:
        assert response.status == 200

    async with app['engine'].acquire() as conn:
        query = accounts.table.count().where(
            accounts.table.c.id == account['id'])
        count = await conn.scalar(query)
        assert count == 0
