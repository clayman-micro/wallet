import pytest

from wallet.storage import categories
from wallet.utils.db import Connection

from . import create_owner, create_category


class TestCategoriesCollection(object):
    owner = {'login': 'John', 'password': 'top_secret'}

    @pytest.mark.run_loop
    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    async def test_get_unauthorized(self, client, headers):
        params = {'endpoint': 'api.get_categories', 'headers': headers}
        async with client.request('GET', **params) as response:
            assert response.status == 401

    @pytest.mark.run_loop
    async def test_get_success(self, app, client):
        owner_id = await create_owner(app, self.owner)

        category = {'name': 'Food', 'owner_id': owner_id}
        category_id = await create_category(app, category)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.get_categories'
        }
        async with client.request('GET', **params) as response:
            assert response.status == 200

            expected = {'id': category_id, 'name': 'Food', 'owner_id': owner_id}

            result = await response.json()
            assert 'categories' in result
            assert result['categories'] == [expected, ]

    @pytest.mark.run_loop
    async def test_get_success_only_for_owner(self, app, client):
        owner = await create_owner(app, self.owner)

        await create_category(app, {'name': 'Food', 'owner_id': owner})

        another_owner = {'login': 'Paul', 'password': 'top_secret'}
        await create_owner(app, another_owner)

        token = await client.get_auth_token(another_owner)
        params = {
            'headers': {'X-ACCESS-TOKEN': token},
            'endpoint': 'api.get_categories'
        }

        async with client.request('GET', **params) as response:
            assert response.status == 200

            data = await response.json()
            assert 'categories' in data
            assert data['categories'] == []

    @pytest.mark.run_loop
    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    async def test_create_unauthorized(self, app, client, headers):
        await create_owner(app, self.owner)

        params = {
            'data': {'name': 'Food'},
            'headers': headers,
            'endpoint': 'api.create_category'
        }
        async with client.request('POST', **params) as response:
            assert response.status == 401

    @pytest.mark.run_loop
    @pytest.mark.parametrize('params', ({'json': False}, {'json': True}))
    async def test_create_success(self, app, client, params):
        owner_id = await create_owner(app, self.owner)

        params['headers'] = {
            'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
        }
        params['data'] = {'name': 'Food'}
        params['endpoint'] = 'api.create_category'

        async with client.request('POST', **params) as response:
            assert response.status == 201

            expected = {'id': 1, 'name': 'Food', 'owner_id': owner_id}

            result = await response.json()
            assert 'category' in result
            assert result['category'] == expected


class TestCategoryResource(object):
    owner = {'login': 'John', 'password': 'top_secret'}

    @pytest.mark.run_loop
    @pytest.mark.parametrize('method,endpoint,headers', (
        ('GET', 'api.get_category', {}),
        ('GET', 'api.get_category', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('PUT', 'api.update_category', {}),
        ('PUT', 'api.update_category', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('DELETE', 'api.remove_category', {}),
        ('DELETE', 'api.remove_category', {'X-ACCESS-TOKEN': 'fake-token'})
    ))
    async def test_unauthorized(self, app, client, method, endpoint, headers):
        owner_id = await create_owner(app, self.owner)

        category_id = await create_category(
            app, {'name': 'Food', 'owner_id': owner_id})

        params = {
            'headers': headers,
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': category_id}
        }
        async with client.request(method, **params) as response:
            assert response.status == 401

    @pytest.mark.run_loop
    @pytest.mark.parametrize('method,endpoint', (
            ('GET', 'api.get_account'),
            ('PUT', 'api.update_account'),
            ('DELETE', 'api.remove_account'),
    ))
    async def test_does_not_belong(self, app, client, method, endpoint):
        owner_id = await create_owner(app, self.owner)

        category_id = await create_category(
            app, {'name': 'Food', 'owner_id': owner_id})

        another_owner = {'login': 'Sam', 'password': 'top_secret'}
        await create_owner(app, another_owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(another_owner)
            },
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': category_id}
        }
        async with client.request(method, **params) as response:
            assert response.status == 404

    @pytest.mark.run_loop
    @pytest.mark.parametrize('method,endpoint', (
            ('GET', 'api.get_account'),
            ('PUT', 'api.update_account'),
            ('DELETE', 'api.remove_account')
    ))
    async def test_missing(self, app, client, method, endpoint):
        await create_owner(app, self.owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': 1}
        }
        async with client.request(method, **params) as response:
            assert response.status == 404

    @pytest.mark.run_loop
    async def test_get_success(self, app, client):
        owner_id = await create_owner(app, self.owner)

        category = {'name': 'Food', 'owner_id': owner_id}
        category_id = await create_category(app, category)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.get_category',
            'endpoint_params': {'instance_id': category_id}
        }
        async with client.request('GET', **params) as response:
            assert response.status == 200

            expected = {'id': 1, 'name': 'Food', 'owner_id': owner_id}

            data = await response.json()
            assert 'category' in data
            assert expected == data['category']

    @pytest.mark.run_loop
    async def test_update_success(self, app, client):
        owner_id = await create_owner(app, self.owner)

        category = {'name': 'Food', 'owner_id': owner_id}
        category_id = await create_category(app, category)

        params = {
            'data': {'name': 'Car'},
            'json': True,
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.update_category',
            'endpoint_params': {'instance_id': category_id}
        }
        async with client.request('PUT', **params) as response:
            assert response.status == 200

            expected = {'id': 1, 'name': 'Car', 'owner_id': owner_id}

            result = await response.json()
            assert result['category'] == expected

    @pytest.mark.run_loop
    async def test_remove_success(self, app, client):
        owner_id = await create_owner(app, self.owner)

        category = {'name': 'Food', 'owner_id': owner_id}
        category_id = await create_category(app, category)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.remove_category',
            'endpoint_params': {'instance_id': category_id}
        }
        async with client.request('DELETE', **params) as response:
            assert response.status == 200

        async with Connection(app['engine']) as conn:
            query = categories.table.count().where(
                categories.table.c.id == category_id)
            count = await conn.scalar(query)
            assert count == 0
