import pytest

from wallet.storage import accounts, transactions

from . import create_owner, create_account, create_category


class TestAccountCollection(object):
    owner = {'login': 'John', 'password': 'top_secret'}

    async def create_account(self, app, account):
        owner_id = await create_owner(app, self.owner)
        account.setdefault('owner_id', owner_id)
        return await create_account(app, account)

    @pytest.mark.run_loop
    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    async def test_get_unauthorized(self, client, headers):
        params = {'headers': headers, 'endpoint': 'api.get_accounts'}
        async with client.request('GET', **params) as response:
            assert response.status == 401

    @pytest.mark.run_loop
    async def test_get_success(self, app, client):
        account_id = await self.create_account(app, {
            'name': 'Credit card', 'original_amount': 30000.0
        })

        token = await client.get_auth_token(self.owner)
        params = {
            'headers': {'X-ACCESS-TOKEN': token},
            'endpoint': 'api.get_accounts'
        }
        async with client.request('GET', **params) as response:
            assert response.status == 200

            expected = {'id': account_id, 'name': 'Credit card',
                        'original_amount': 30000.0, 'current_amount': 30000.0}

            data = await response.json()
            assert 'accounts' in data
            assert data['accounts'] == [expected, ]

    @pytest.mark.run_loop
    async def test_get_success_only_for_owner(self, app, client):
        await self.create_account(app, {
            'name': 'Credit card', 'original_amount': 30000.0
        })

        another_owner = {'login': 'Paul', 'password': 'top_secret'}
        await create_owner(app, another_owner)

        token = await client.get_auth_token(another_owner)
        params = {
            'headers': {'X-ACCESS-TOKEN': token},
            'endpoint': 'api.get_accounts'
        }
        async with client.request('GET', **params) as response:
            assert response.status == 200

            data = await response.json()
            assert 'accounts' in data
            assert data['accounts'] == []

    @pytest.mark.run_loop
    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    async def test_create_unauthorized(self, app, server, client, headers):
        await create_owner(app, self.owner)
        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0}

        params = {
            'data': account,
            'headers': headers,
            'endpoint': 'api.create_account'
        }
        async with client.request('GET', **params) as response:
            assert response.status == 401

    @pytest.mark.run_loop
    @pytest.mark.parametrize('params', ({'json': False}, {'json': True}))
    async def test_create_success(self, app, client, params):
        await create_owner(app, self.owner)

        token = await client.get_auth_token(self.owner)
        params['headers'] = {'X-ACCESS-TOKEN': token}
        params['data'] = {'name': 'Credit card', 'original_amount': 30000.0}
        params['endpoint'] = 'api.create_account'

        async with client.request('POST', **params) as response:
            assert response.status == 201

            expected = {'id': 1, 'name': 'Credit card',
                        'original_amount': 30000.0, 'current_amount': 30000.0}

            response = await response.json()
            assert 'account' in response
            assert expected == response['account']


class TestAccountResource(object):
    owner = {'login': 'John', 'password': 'top_secret'}

    @pytest.mark.run_loop
    @pytest.mark.parametrize('method,endpoint,headers', (
        ('GET', 'api.get_account', {}),
        ('GET', 'api.get_account', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('PUT', 'api.update_account', {}),
        ('PUT', 'api.update_account', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('DELETE', 'api.remove_account', {}),
        ('DELETE', 'api.remove_account', {'X-ACCESS-TOKEN': 'fake-token'}),
    ))
    async def test_unauthorized(self, app, client, method, endpoint, headers):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = await create_owner(app, owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = await create_account(app, account)

        params = {
            'headers': headers,
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': account_id}
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
        account_id = await create_account(app, {
            'name': 'Credit card', 'original_amount': 30000.0,
            'current_amount': 0.0,'owner_id': owner_id
        })

        another_owner = {'login': 'Sam', 'password': 'top_secret'}
        await create_owner(app, another_owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(another_owner)
            },
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': account_id}
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

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = await create_account(app, account)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.get_account',
            'endpoint_params': {'instance_id': account_id}
        }

        async with client.request('GET', **params) as response:
            assert response.status == 200

            expected = {'id': 1, 'name': 'Credit card',
                        'original_amount': 30000.0, 'current_amount': 0.0}

            data = await response.json()
            assert 'account' in data
            assert expected == data['account']

    @pytest.mark.run_loop
    async def test_update_success(self, app, client):
        owner_id = await create_owner(app, self.owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 2000.0, 'owner_id': owner_id}
        account_id = await create_account(app, account)

        params = {
            'data': {'name': 'Debit card'},
            'json': True,
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.update_account',
            'endpoint_params': {'instance_id': account_id}
        }
        async with client.request('PUT', **params) as response:
            assert response.status == 200

            expected = {'id': 1, 'name': 'Debit card',
                        'original_amount': 30000.0, 'current_amount': 2000.0}

            response = await response.json()
            assert expected == response['account']

    @pytest.mark.run_loop
    @pytest.mark.parametrize('json', (False, True))
    async def test_update_current_amount(self, app, client, json):
        owner_id = await create_owner(app, self.owner)
        category_id = await create_category(
            app, {'name': 'Food', 'owner_id': owner_id})
        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 10000.0, 'owner_id': owner_id}
        account_id = await create_account(app, account)

        headers = {'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)}
        items = [{
            'description': 'Meal', 'amount': 1000.0,
            'type': transactions.EXPENSE_TRANSACTION,
            'account_id': account_id, 'category_id': category_id,
            'created_on': '2015-08-20T00:00:00'
        }, {
            'description': 'Meal', 'amount': 10000.0,
            'type': transactions.INCOME_TRANSACTION,
            'account_id': account_id, 'category_id': category_id,
            'created_on': '2015-08-20T00:00:00'
        }]

        for item in items:
            params = {
                'json': json, 'data': item, 'headers': headers,
                'endpoint': 'api.create_transaction'
            }
            async with client.request('POST', **params) as response:
                assert response.status == 201

        params = {
            'json': True,
            'data': {'original_amount': 20000.0},
            'headers': headers,
            'endpoint': 'api.update_account',
            'endpoint_params': {'instance_id': account_id}
        }
        async with client.request('PUT', **params) as response:
            assert response.status == 200

            expected = {'id': 1, 'name': 'Credit card',
                        'original_amount': 20000.0, 'current_amount': 29000.0}

            result = await response.json()
            assert expected == result['account']

    @pytest.mark.run_loop
    @pytest.mark.parametrize('data', ({'owner_id': 2}, {'current_amount': 10}))
    async def test_update_readonly(self, app, client, data):
        owner_id = await create_owner(app, self.owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = await create_account(app, account)

        params = {
            'data': data,
            'json': True,
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.update_account',
            'endpoint_params': {'instance_id': account_id}
        }
        async with client.request('PUT', **params) as response:
            assert response.status == 400

    @pytest.mark.run_loop
    async def test_remove_success(self, app, client):
        owner_id = await create_owner(app, self.owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = await create_account(app, account)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.remove_account',
            'endpoint_params': {'instance_id': account_id}
        }
        async with client.request('DELETE', **params) as response:
            assert response.status == 200

        async with app['engine'].acquire() as conn:
            query = accounts.table.count().where(
                accounts.table.c.id == account_id)
            count = await conn.scalar(query)
            assert count == 0
