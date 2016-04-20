import pytest

from wallet.storage import details

from . import create_detail


@pytest.mark.run_loop
@pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
@pytest.mark.parametrize('method, endpoint, params', [
    ('GET', 'api.get_details', {'transaction_id': 1, }),
    ('POST', 'api.create_detail', {'transaction_id': 1, }),
    ('GET', 'api.get_detail', {'transaction_id': 1, 'instance_id': 1}),
    ('PUT', 'api.update_detail', {'transaction_id': 1, 'instance_id': 1}),
    ('DELETE', 'api.remove_detail', {'transaction_id': 1, 'instance_id': 1})
])
async def test_unauthorized(client, headers, method, endpoint, params):
    params = {'headers': headers, 'endpoint': endpoint, 'endpoint_params': params}
    async with client.request(method, **params) as response:
        assert response.status == 401


@pytest.mark.run_loop
async def test_collection(app, client, transaction):
    detail = await create_detail({
        'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0, 'total': 300.0,
        'transaction_id': transaction['id']
    }, app=app)

    params = await client.get_params('api.get_details',
                                     transaction['owner']['credentials'])
    params['endpoint_params'] = {'transaction_id': transaction['id']}
    async with client.request('GET', **params) as response:
        assert response.status == 200
        data = await response.json()
        assert 'details' in data
        assert data['details'] == [{
            'id': detail['id'], 'name': 'Soup', 'price_per_unit': 300.0,
            'count': 1.0, 'transaction_id': transaction['id'], 'total': 300.0
        }, ]


@pytest.mark.run_loop
async def test_collection_access_for_stranger(app, client, transaction,
                                              stranger):
    await create_detail({
        'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0, 'total': 300.0,
        'transaction_id': transaction['id']
    }, app=app)

    params = await client.get_params('api.get_details', stranger['credentials'])
    params['endpoint_params'] = {'transaction_id': transaction['id']}
    async with client.request('GET', **params) as response:
        assert response.status == 404


@pytest.mark.run_loop
@pytest.mark.parametrize('json', (True, False))
async def test_create(client, transaction, json):
    params = await client.get_params('api.create_detail',
                                     transaction['owner']['credentials'])
    params.update(endpoint_params={'transaction_id': transaction['id']},
                  data={'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                        'total': 300.0}, json=json)
    async with client.request('POST', **params) as response:
        assert response.status == 201
        result = await response.json()
        assert 'detail' in result
        assert result['detail'] == {
            'id': 1, 'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
            'total': 300.0, 'transaction_id': transaction['id']
        }


@pytest.mark.run_loop
@pytest.mark.parametrize('method, endpoint', (
    ('GET', 'api.get_account'),
    ('PUT', 'api.update_account'),
    ('DELETE', 'api.remove_account')
))
async def test_missing(client, transaction, method, endpoint):
    params = params = await client.get_params('api.get_detail',
                                              transaction['owner']['credentials'])
    params['endpoint_params'] = {'transaction_id': transaction['id'],
                                 'instance_id': 1}
    async with client.request(method, **params) as response:
        assert response.status == 404


@pytest.mark.run_loop
@pytest.mark.parametrize('method, endpoint', (
    ('GET', 'api.get_account'),
    ('PUT', 'api.update_account'),
    ('DELETE', 'api.remove_account')
))
async def test_missing(client, transaction, stranger, method, endpoint):
    params = await client.get_params(endpoint, stranger['credentials'])
    params['endpoint_params'] = {'transaction_id': transaction['id'],
                                 'instance_id': 1}
    async with client.request(method, **params) as response:
        assert response.status == 404


@pytest.mark.run_loop
async def test_get_resource(app, client, transaction):
    detail = await create_detail({
        'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0, 'total': 300.0,
        'transaction_id': transaction['id']
    }, app=app)

    params = await client.get_params('api.get_detail',
                                     transaction['owner']['credentials'])
    params['endpoint_params'] = {'transaction_id': transaction['id'],
                                 'instance_id': detail['id']}
    async with client.request('GET', **params) as response:
        assert response.status == 200
        data = await response.json()
        assert 'detail' in data
        assert data['detail'] == {
            'id': detail['id'], 'name': 'Soup', 'price_per_unit': 300.0,
            'count': 1.0, 'transaction_id': transaction['id'], 'total': 300.0
        }


@pytest.mark.run_loop
@pytest.mark.parametrize('json', (True, False))
async def test_update_resource(app, client, transaction, json):
    detail = await create_detail({
        'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0, 'total': 300.0,
        'transaction_id': transaction['id']
    }, app=app)

    params = await client.get_params('api.update_detail',
                                     transaction['owner']['credentials'])
    params.update(endpoint_params={'transaction_id': transaction['id'],
                                   'instance_id': detail['id']},
                  data={'price_per_unit': 100.0}, json=json)
    async with client.request('PUT', **params) as response:
        assert response.status == 200
        data = await response.json()
        assert 'detail' in data
        assert data['detail'] == {
            'id': detail['id'], 'name': 'Soup', 'price_per_unit': 100.0,
            'count': 1.0, 'transaction_id': transaction['id'], 'total': 100.0
        }


@pytest.mark.run_loop
async def test_remove_resource(app, client, transaction):
    detail = await create_detail({
        'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0, 'total': 300.0,
        'transaction_id': transaction['id']
    }, app=app)

    params = await client.get_params('api.remove_detail',
                                     transaction['owner']['credentials'])
    params.update(endpoint_params={'transaction_id': transaction['id'],
                                   'instance_id': detail['id']})
    async with client.request('DELETE', **params) as response:
        assert response.status == 200

    async with app['engine'].acquire() as conn:
        query = details.table.count().where(
            details.table.c.id == detail.get('id'))
        count = await conn.scalar(query)
        assert count == 0