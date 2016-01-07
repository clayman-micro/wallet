from datetime import datetime

import pytest

from wallet.storage import transactions, details
from wallet.utils.db import Connection

from . import (create_owner, create_account, create_category,
               create_transaction, create_detail)


class BaseTransactionTest(object):
    owner = {'login': 'John', 'password': 'top_secret'}
    account = {'name': 'Credit card', 'original_amount': 30000.0}
    category = {'name': 'Food'}
    transaction = {'description': 'Meal', 'amount': 300.0,
                   'type': transactions.EXPENSE_TRANSACTION}

    async def prepare(self, app):
        owner_id = await create_owner(app, self.owner)
        account_id = await create_account(
                app, {**self.account, 'owner_id': owner_id})
        category_id = await create_category(
                app, {**self.category, 'owner_id': owner_id})
        return await create_transaction(
                app, {**self.transaction, 'category_id': category_id,
                      'account_id': account_id})


class TestTransactionCollection(BaseTransactionTest):

    @pytest.mark.run_loop
    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    async def test_get_unauthorized(self, client, headers):
        params = {
            'headers': headers,
            'endpoint': 'api.get_transactions'
        }
        async with client.request('GET', **params) as response:
            assert response.status == 401

    @pytest.mark.run_loop
    async def test_get_success(self, app, client):
        now = datetime.now()
        owner_id = await create_owner(app, self.owner)
        account_id = await create_account(
            app, {**self.account, 'owner_id': owner_id})
        category_id = await create_category(
            app, {**self.category, 'owner_id': owner_id})

        transaction = {
            'description': 'Meal', 'amount': 300.0,
            'type': transactions.INCOME_TRANSACTION, 'created_on': now,
            'account_id': account_id, 'category_id': category_id
        }

        expected = transaction.copy()
        expected['id'] = await create_transaction(app, transaction)
        expected['created_on'] = now.strftime('%Y-%m-%dT%X')

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.get_transactions'
        }

        async with client.request('GET', **params) as response:
            assert response.status == 200

            result = await response.json()
            assert 'transactions' in result
            assert result['transactions'] == [expected, ]

    @pytest.mark.run_loop
    async def test_get_success_only_for_owner(self, app, client):
        owner_id = await create_owner(app, self.owner)
        account_id = await create_account(
            app, {**self.account, 'owner_id': owner_id})
        category_id = await create_category(
           app, {**self.category, 'owner_id': owner_id})
        transaction = {
            'description': 'Meal', 'amount': 300.0,
            'type': transactions.INCOME_TRANSACTION,
            'account_id': account_id, 'category_id': category_id
        }
        await create_transaction(app, transaction)

        another_owner = {'login': 'Samuel', 'password': 'top_secret'}
        await create_owner(app, another_owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(another_owner)
            },
            'endpoint': 'api.get_transactions'
        }

        async with client.request('GET', **params) as response:
            assert response.status == 200

            result = await response.json()
            assert 'transactions' in result
            assert result['transactions'] == []

    @pytest.mark.run_loop
    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    async def test_create_unauthorized(self, app, client, headers):
        owner_id = await create_owner(app, self.owner)
        account_id = await create_account(
            app, {**self.account, 'owner_id': owner_id})
        category_id = await create_category(
            app, {**self.category, 'owner_id': owner_id})

        params = {
            'data': {'description': 'Meal', 'amount': 300.0,
                     'type': transactions.INCOME_TRANSACTION,
                     'account_id': account_id, 'category_id': category_id},
            'headers': headers,
            'endpoint': 'api.create_transaction'
        }
        async with client.request('POST', **params) as response:
            assert response.status == 401

    @pytest.mark.run_loop
    @pytest.mark.parametrize('params', ({'json': False}, {'json': True}))
    async def test_create_success(self, app, client, params):
        owner_id = await create_owner(app, self.owner)
        account_id = await create_account(
            app, {**self.account, 'owner_id': owner_id})
        category_id = await create_category(
            app, {**self.category, 'owner_id': owner_id})

        params.update(
            data={'description': 'Meal', 'amount': 300.0,
                  'type': transactions.INCOME_TRANSACTION,
                  'account_id': account_id, 'category_id': category_id,
                  'created_on': '2015-08-20T00:00:00'},
            headers={'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)},
            endpoint='api.create_transaction'
        )
        async with client.request('POST', **params) as response:
            assert response.status == 201

            expected = {'id': 1, 'description': 'Meal', 'amount': 300.0,
                        'type': transactions.INCOME_TRANSACTION,
                        'account_id': account_id, 'category_id': category_id,
                        'created_on': '2015-08-20T00:00:00'}

            result = await response.json()
            assert 'transaction' in result
            assert result['transaction'] == expected


class TestTransactionResource(BaseTransactionTest):

    @pytest.mark.run_loop
    @pytest.mark.parametrize('method,endpoint,headers', (
        ('GET', 'api.get_transaction', {}),
        ('GET', 'api.get_transaction', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('PUT', 'api.update_transaction', {}),
        ('PUT', 'api.update_transaction', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('DELETE', 'api.remove_transaction', {}),
        ('DELETE', 'api.remove_transaction', {'X-ACCESS-TOKEN': 'fake-token'})
    ))
    async def test_unauthorized(self, app, client, method, endpoint, headers):
        transaction_id = await self.prepare(app)

        params = {
            'headers': headers,
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': transaction_id}
        }
        async with client.request(method, **params) as response:
            assert response.status == 401

    @pytest.mark.run_loop
    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_transaction'),
        ('PUT', 'api.update_transaction'),
        ('DELETE', 'api.remove_transaction')
    ))
    async def test_does_not_belong(self, app, client, method, endpoint):
        transaction_id = await self.prepare(app)

        another_owner = {'login': 'Sam', 'password': 'top_secret'}
        await create_owner(app, another_owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(another_owner)
            },
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': transaction_id}
        }
        async with client.request(method, **params) as response:
            assert response.status == 404

    @pytest.mark.run_loop
    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_transaction'),
        ('PUT', 'api.update_transaction'),
        ('DELETE', 'api.remove_transaction'),
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
    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_transaction'),
        ('PUT', 'api.update_transaction'),
        ('DELETE', 'api.remove_transaction')
    ))
    async def test_wrong_instance_id(self, app, client, method, endpoint):
        await create_owner(app, self.owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': 'undefined'}
        }

        async with client.request(method, **params) as response:
            assert response.status == 400

    @pytest.mark.run_loop
    async def test_get_success(self, app, client):
        now = datetime.now()
        owner_id = await create_owner(app, self.owner)
        account_id = await create_account(
            app, {**self.account, 'owner_id': owner_id})
        category_id = await create_category(
            app, {**self.category, 'owner_id': owner_id})

        transaction = {**self.transaction, 'category_id': category_id,
                       'account_id': account_id, 'created_on': now}

        expected = transaction.copy()
        expected['id'] = await create_transaction(app, transaction)
        expected['created_on'] = now.strftime('%Y-%m-%dT%X')

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.get_transaction',
            'endpoint_params': {'instance_id': expected.get('id')}
        }
        async with client.request('GET', **params) as response:
            assert response.status == 200

            data = await response.json()
            assert 'transaction' in data
            assert expected == data['transaction']

    @pytest.mark.run_loop
    async def test_update_success(self, app, client):
        now = datetime.now()
        owner_id = await create_owner(app, self.owner)
        account_id = await create_account(
            app, {**self.account, 'owner_id': owner_id})
        category_id = await create_category(
            app, {**self.category, 'owner_id': owner_id})

        transaction = {**self.transaction, 'category_id': category_id,
                       'account_id': account_id, 'created_on': now}

        expected = transaction.copy()
        expected['id'] = await create_transaction(app, transaction)
        expected['amount'] = 310.0
        expected['created_on'] = now.strftime('%Y-%m-%dT%X')

        params = {
            'data': {'amount': '310'},
            'json': True,
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.update_transaction',
            'endpoint_params': {'instance_id': expected.get('id')}
        }

        async with client.request('PUT', **params) as response:
            assert response.status == 200

            result = await response.json()
            assert 'transaction' in result
            assert result['transaction'] == expected

    @pytest.mark.run_loop
    async def test_remove_success(self, app, client):
        transaction_id = await self.prepare(app)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.remove_transaction',
            'endpoint_params': {'instance_id': transaction_id}
        }
        async with client.request('DELETE', **params) as response:
            assert response.status == 200

        async with Connection(app['engine']) as conn:
            query = transactions.table.count().where(
                transactions.table.c.id == transaction_id)
            count = await conn.scalar(query)
            assert count == 0


class TestTransactionDetailsCollection(BaseTransactionTest):

    @pytest.mark.run_loop
    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    async def test_get_unauthorized(self, app, client, headers):
        transaction_id = await self.prepare(app)

        params = {
            'headers': headers,
            'endpoint': 'api.get_details',
            'endpoint_params': {'transaction_id': transaction_id}
        }
        async with client.request('GET', **params) as response:
            assert response.status == 401

    @pytest.mark.run_loop
    async def test_get_success(self, app, client):
        transaction_id = await self.prepare(app)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0, 'transaction_id': transaction_id}
        detail_id = await create_detail(app, detail)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.get_details',
            'endpoint_params': {'transaction_id': transaction_id}
        }

        async with client.request('GET', **params) as response:
            assert response.status == 200

            expected = {'id': detail_id, 'name': 'Soup',
                        'price_per_unit': 300.0, 'count': 1.0,
                        'transaction_id': transaction_id,
                        'total': 300.0}

            result = await response.json()
            assert 'details' in result
            assert result['details'] == [expected, ]

    @pytest.mark.run_loop
    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_details'),
        ('POST', 'api.create_detail')
    ))
    async def test_for_not_owner_transaction(self, app, client, method, endpoint):
        transaction_id = await self.prepare(app)

        another_owner = {'login': 'Samuel', 'password': 'top_secret'}
        await create_owner(app, another_owner)

        token = await client.get_auth_token(another_owner)
        params = {
            'headers': {'X-ACCESS-TOKEN': token},
            'endpoint': endpoint,
            'endpoint_params': {'transaction_id': transaction_id}
        }
        async with client.request(method, **params) as response:
            assert response.status == 404

    @pytest.mark.run_loop
    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_details'),
        ('POST', 'api.create_detail')
    ))
    async def test_for_missing_transaction(self, app, client, method, endpoint):
        await self.prepare(app)
        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': endpoint, 'endpoint_params': {'transaction_id': 2}
        }
        async with client.request(method, **params) as response:
            assert response.status == 404

    @pytest.mark.run_loop
    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    async def test_create_unauthorized(self, app, client, headers):
        transaction_id = await self.prepare(app)

        params = {
            'data': {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                     'total': 300.0, 'transaction_id': transaction_id},
            'headers': headers,
            'endpoint': 'api.create_detail',
            'endpoint_params': {'transaction_id': transaction_id}
        }
        async with client.request('POST', **params) as response:
            assert response.status == 401

    @pytest.mark.run_loop
    @pytest.mark.parametrize('params', ({'json': True}, {'json': False}))
    async def test_create_success(self, app, client, params):
        transaction_id = await self.prepare(app)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0}

        params.update(
            headers={
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            data=detail, endpoint='api.create_detail', endpoint_params={
                'transaction_id': transaction_id
            }
        )
        async with client.request('POST', **params) as response:
            assert response.status == 201

            expected = {'id': 1, 'name': 'Soup',
                        'transaction_id': transaction_id,
                        'price_per_unit': 300.0, 'count': 1.0, 'total': 300.0}

            result = await response.json()
            assert 'detail' in result
            assert result['detail'] == expected

    @pytest.mark.run_loop
    @pytest.mark.parametrize('params', ({'json': True}, {'json': False}))
    async def test_create_for_foreign(self, app, client, params):
        transaction_id = await self.prepare(app)

        another_owner = {'login': 'Sam', 'password': 'top_secret'}
        await create_owner(app, another_owner)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0}

        params.update(
            headers={
                'X-ACCESS-TOKEN': await client.get_auth_token(another_owner)
            },
            data=detail, endpoint='api.create_detail', endpoint_params={
                'transaction_id': transaction_id
            }
        )
        async with client.request('POST', **params) as response:
            assert response.status == 404


class TestTransactionDetailsResource(BaseTransactionTest):

    @pytest.mark.run_loop
    @pytest.mark.parametrize('method,endpoint,headers', (
        ('GET', 'api.get_detail', {}),
        ('GET', 'api.get_detail', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('PUT', 'api.update_detail', {}),
        ('PUT', 'api.update_detail', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('DELETE', 'api.remove_detail', {}),
        ('DELETE', 'api.remove_detail', {'X-ACCESS-TOKEN': 'fake-token'})
    ))
    async def test_unauthorized(self, app, client, method, endpoint, headers):
        transaction_id = await self.prepare(app)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0, 'transaction_id': transaction_id}
        detail_id = await create_detail(app, detail)

        params = {
            'headers': headers,
            'endpoint': endpoint,
            'endpoint_params': {
                'transaction_id': transaction_id, 'instance_id': detail_id
            }
        }
        async with client.request(method, **params) as response:
            assert response.status == 401

    @pytest.mark.run_loop
    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_detail'),
        ('PUT', 'api.update_detail'),
        ('DELETE', 'api.remove_detail')
    ))
    async def test_does_not_belong(self, app, client, method, endpoint):
        transaction_id = await self.prepare(app)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0, 'transaction_id': transaction_id}
        detail_id = await create_detail(app, detail)

        another_owner = {'login': 'Sam', 'password': 'top_secret'}
        await create_owner(app, another_owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(another_owner)
            },
            'endpoint': endpoint,
            'endpoint_params': {
                'instance_id': detail_id, 'transaction_id': transaction_id
            }
        }
        async with client.request(method, **params) as response:
            assert response.status == 404

    @pytest.mark.run_loop
    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_detail'),
        ('PUT', 'api.update_detail'),
        ('DELETE', 'api.remove_detail')
    ))
    async def test_missing(self, app, client, method, endpoint):
        transaction_id = await self.prepare(app)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': endpoint,
            'endpoint_params': {
                'transaction_id': transaction_id, 'instance_id': 1
            }
        }
        async with client.request(method, **params) as response:
            assert response.status == 404

    @pytest.mark.run_loop
    async def test_get_success(self, app, client):
        transaction_id = await self.prepare(app)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0, 'transaction_id': transaction_id}
        detail_id = await create_detail(app, detail)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.get_detail',
            'endpoint_params': {
                'transaction_id': transaction_id, 'instance_id': detail_id
            }
        }
        async with client.request('GET', **params) as response:
            assert response.status == 200

            detail['id'] = detail_id

            result = await response.json()
            assert 'detail' in result
            assert detail == result['detail']

    @pytest.mark.run_loop
    async def test_update_success(self, app, client):
        transaction_id = await self.prepare(app)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0, 'transaction_id': transaction_id}
        detail_id = await create_detail(app, detail)

        params = {
            'data': {'price_per_unit': 270.0},
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.update_detail',
            'endpoint_params': {
                'transaction_id': transaction_id, 'instance_id': detail_id
            }
        }

        detail['id'] = detail_id
        detail['price_per_unit'] = 270.0
        detail['total'] = 270.0

        async with client.request('PUT', **params) as response:
            assert response.status == 200

            result = await response.json()
            assert 'detail' in result
            assert detail == result['detail']

    @pytest.mark.run_loop
    async def test_remove_success(self, app, client):
        transaction_id = await self.prepare(app)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0, 'transaction_id': transaction_id}
        detail_id = await create_detail(app, detail)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': await client.get_auth_token(self.owner)
            },
            'endpoint': 'api.remove_detail',
            'endpoint_params': {
                'transaction_id': transaction_id, 'instance_id': detail_id
            }
        }
        async with client.request('DELETE', **params) as resp:
            assert resp.status == 200

        async with Connection(app['engine']) as conn:
            query = details.table.count().where(
                details.table.c.id == detail.get('id'))
            count = await conn.scalar(query)
            assert count == 0
