import pytest

from wallet.storage import categories

from . import create_owner, create_category


@pytest.mark.run_loop
@pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
@pytest.mark.parametrize('method, endpoint, endpoint_params', [
    ('GET', 'api.get_categories', None),
    ('POST', 'api.create_category', None),
    ('GET', 'api.get_category', {'instance_id': 1}),
    ('PUT', 'api.update_category', {'instance_id': 1}),
    ('DELETE', 'api.remove_category', {'instance_id': 1})
])
async def test_unauthorized(client, headers, method, endpoint, endpoint_params):
    params = {'headers': headers, 'endpoint': endpoint,
              'endpoint_params': endpoint_params}
    async with client.request(method, **params) as response:
        assert response.status == 401


@pytest.mark.run_loop
async def test_collection(app, client, owner):
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app)

    params = await client.get_params('api.get_categories', owner['credentials'])
    async with client.request('GET', **params) as response:
        assert response.status == 200
        result = await response.json()
        assert 'categories' in result
        assert result['categories'] == [{'id': category['id'], 'name': 'Food'}, ]


@pytest.mark.run_loop
async def test_collection_only_for_owner(app, client, owner, stranger):
    await create_category({'name': 'Food', 'owner_id': owner['id']}, app)

    params = await client.get_params('api.get_categories', stranger['credentials'])
    async with client.request('GET', **params) as response:
        assert response.status == 200
        result = await response.json()
        assert 'categories' in result
        assert len(result['categories']) == 0


@pytest.mark.run_loop
@pytest.mark.parametrize('json', (True, False))
async def test_create(app, client, owner, json):
    params = await client.get_params('api.create_category', owner['credentials'])
    params.update(data={'name': 'Food'}, json=json)

    async with client.request('POST', **params) as response:
        assert response.status == 201
        result = await response.json()
        assert 'category' in result
        assert result['category'] == {'id': 1, 'name': 'Food'}


@pytest.mark.run_loop
@pytest.mark.parametrize('json', (True, False))
async def test_create_with_name_conflict(app, client, owner, json):
    await create_category({'name': 'Food', 'owner_id': owner['id']}, app)

    params = await client.get_params('api.create_category', owner['credentials'])
    params.update(data={'name': 'Food'}, json=json)

    async with client.request('POST', **params) as response:
        assert response.status == 400
        result = await response.json()
        assert 'errors' in result
        assert 'name' in result['errors']


@pytest.mark.run_loop
@pytest.mark.parametrize('method, endpoint', (
    ('GET', 'api.get_category'),
    ('PUT', 'api.update_category'),
    ('DELETE', 'api.remove_category')
))
async def test_missing(client, owner, method, endpoint):
    params = await client.get_params(endpoint, owner['credentials'], 1)
    async with client.request(method, **params) as response:
        assert response.status == 404


@pytest.mark.run_loop
@pytest.mark.parametrize('method, endpoint', (
    ('GET', 'api.get_category'),
    ('PUT', 'api.update_category'),
    ('DELETE', 'api.remove_category')
))
async def test_access_for_strangers(app, client, owner, stranger, method,
                                    endpoint):
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app)

    params = await client.get_params(endpoint, stranger['credentials'],
                                     category['id'])

    async with client.request(method, **params) as response:
        assert response.status == 404


@pytest.mark.run_loop
async def test_get_resource(app, client, owner):
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app=app)

    params = await client.get_params('api.get_category', owner['credentials'],
                                     category['id'])

    async with client.request('GET', **params) as response:
        assert response.status == 200

        data = await response.json()
        assert 'category' in data
        assert data['category'] == {'id': 1, 'name': 'Food'}


@pytest.mark.run_loop
@pytest.mark.parametrize('json', (True, False))
async def test_update_resource(app, client, owner, json):
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app=app)

    params = await client.get_params('api.update_category', owner['credentials'],
                                     category['id'])
    params.update(data={'name': 'Supermarket'}, json=json)

    async with client.request('PUT', **params) as response:
        assert response.status == 200

        data = await response.json()
        assert 'category' in data
        assert data['category'] == {'id': 1, 'name': 'Supermarket'}


@pytest.mark.run_loop
async def test_remove_resource(app, client, owner):
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app=app)

    params = await client.get_params('api.remove_category', owner['credentials'],
                                     category['id'])

    async with client.request('DELETE', **params) as response:
        assert response.status == 200

    async with app['engine'].acquire() as conn:
        query = categories.table.count().where(
            categories.table.c.id == category['id'])
        count = await conn.scalar(query)
        assert count == 0
