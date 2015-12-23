import pytest

from wallet.storage import accounts

from tests.conftest import async_test
from . import BaseHandlerTest


class TestAccountCollection(BaseHandlerTest):

    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    @async_test(create_database=True)
    def test_get_unauthorized(self, application, server, headers, **kwargs):
        params = {
            'headers': headers,
            'url': server.reverse_url('api.get_accounts')
        }
        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 401

    @async_test(create_database=True)
    def test_get_success(self, application, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)
        token = yield from server.get_auth_token(owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = yield from self.create_account(application, account)

        params = {
            'headers': {'X-ACCESS-TOKEN': token},
            'url': server.reverse_url('api.get_accounts')
        }

        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 200

            expected = {'id': account_id, 'name': 'Credit card',
                        'original_amount': 30000.0, 'current_amount': 0.0}

            data = yield from response.json()
            assert 'accounts' in data
            assert [expected, ] == data['accounts']

    @async_test(create_database=True)
    def test_get_success_only_for_owner(self, application, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        yield from self.create_account(application, account)

        another_owner = {'login': 'Paul', 'password': 'top_secret'}
        yield from self.create_owner(application, another_owner)
        token = yield from server.get_auth_token(another_owner)

        params = {
            'headers': {'X-ACCESS-TOKEN': token},
            'url': server.reverse_url('api.get_accounts')
        }

        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 200

            data = yield from response.json()
            assert 'accounts' in data
            assert data['accounts'] == []

    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    @async_test(create_database=True)
    def test_create_unauthorized(self, application, headers, server):
        owner = {'login': 'Paul', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}

        params = {
            'data': account,
            'headers': headers,
            'url': server.reverse_url('api.create_account')
        }
        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 401

    @pytest.mark.parametrize('params', ({'json': False}, {'json': True}))
    @async_test(create_database=True)
    def test_create_success(self, application, params, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        token = yield from server.get_auth_token({'login': 'John',
                                                  'password': 'top_secret'})

        params['headers'] = {'X-ACCESS-TOKEN': token}
        params['data'] = {'name': 'Credit card', 'original_amount': 30000.0}
        params['url'] = server.reverse_url('api.create_account')

        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 201

            expected = {'id': 1, 'name': 'Credit card',
                        'original_amount': 30000.0, 'current_amount': 30000.0}

            response = yield from response.json()
            assert 'account' in response
            assert expected == response['account']


class TestAccountResource(BaseHandlerTest):

    @pytest.mark.parametrize('method,endpoint,headers', (
        ('GET', 'api.get_account', {}),
        ('GET', 'api.get_account', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('PUT', 'api.update_account', {}),
        ('PUT', 'api.update_account', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('DELETE', 'api.remove_account', {}),
        ('DELETE', 'api.remove_account', {'X-ACCESS-TOKEN': 'fake-token'}),
    ))
    @async_test(create_database=True)
    def test_unauthorized(self, application, method, endpoint, headers, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = yield from self.create_account(application, account)

        params = {
            'headers': headers,
            'url': server.reverse_url(endpoint, {'instance_id': account_id})
        }
        with (yield from server.response_ctx(method, **params)) as response:
            assert response.status == 401

    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_account'),
        ('PUT', 'api.update_account'),
        ('DELETE', 'api.remove_account'),
    ))
    @async_test(create_database=True)
    def test_does_not_belong(self, application, method, endpoint, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = yield from self.create_account(application, account)

        another_owner = {'login': 'Sam', 'password': 'top_secret'}
        yield from self.create_owner(application, another_owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(another_owner))
            },
            'url': server.reverse_url(endpoint, {'instance_id': account_id})
        }
        with (yield from server.response_ctx(method, **params)) as response:
            assert response.status == 404

    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_account'),
        ('PUT', 'api.update_account'),
        ('DELETE', 'api.remove_account')
    ))
    @async_test(create_database=True)
    def test_missing(self, application, method, endpoint, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        yield from self.create_owner(application, owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url(endpoint, {'instance_id': 1})
        }
        with (yield from server.response_ctx(method, **params)) as response:
            assert response.status == 404

    @async_test(create_database=True)
    def test_get_success(self, application, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = yield from self.create_account(application, account)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.get_account',
                                      {'instance_id': account_id})
        }
        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 200

            expected = {'id': 1, 'name': 'Credit card',
                        'original_amount': 30000.0, 'current_amount': 0.0}

            data = yield from response.json()
            assert 'account' in data
            assert expected == data['account']

    @async_test(create_database=True)
    def test_update_success(self, application, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = yield from self.create_account(application, account)

        params = {
            'data': {'name': 'Debit card'},
            'json': True,
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.update_account',
                                      {'instance_id': account_id})
        }
        with (yield from server.response_ctx('PUT', **params)) as resp:
            assert resp.status == 200

            expected = {'id': 1, 'name': 'Debit card',
                        'original_amount': 30000.0, 'current_amount': 0.0}

            response = yield from resp.json()
            assert expected == response['account']

    @async_test(create_database=True)
    def test_update_owner(self, application, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = yield from self.create_account(application, account)

        params = {
            'data': {'owner_id': 2},
            'json': True,
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.update_account',
                                      {'instance_id': account_id})
        }
        with (yield from server.response_ctx('PUT', **params)) as resp:
            assert resp.status == 400

    @async_test(create_database=True)
    def test_remove_success(self, application, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = yield from self.create_account(application, account)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.remove_account',
                                      {'instance_id': account_id})
        }
        with (yield from server.response_ctx('DELETE', **params)) as response:
            assert response.status == 200

        with (yield from application['engine']) as conn:
            query = accounts.table.count().where(
                accounts.table.c.id == account_id)
            count = yield from conn.scalar(query)
            assert count == 0
