import asyncio
from datetime import datetime

import pytest

from wallet.models import categories, transactions

from tests.conftest import async_test
from . import BaseHandlerTest


class BaseTransactionTest(BaseHandlerTest):

    @asyncio.coroutine
    def prepare_data(self, app, transaction=None):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(app, owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = yield from self.create_account(app, account)

        category = {'name': 'Food', 'owner_id': owner_id}
        category_id = yield from self.create_instance(
            app, categories.categories_table, category)

        if transaction:
            transaction.setdefault('account_id', account_id)
            transaction.setdefault('category_id', category_id)
            transaction.setdefault('created_on', datetime.now())

            transaction_id = yield from self.create_instance(
                app, transactions.transactions_table, transaction)

            del transaction['created_on']
            transaction['id'] = transaction_id
            return owner, transaction

        return owner, account_id, category_id


class TestTransactionCollection(BaseTransactionTest):

    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    @async_test(create_database=True)
    def test_get_unauthorized(self, application, headers, server):
        params = {
            'headers': headers,
            'url': server.reverse_url('api.get_transactions')
        }
        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 401

    @async_test(create_database=True)
    def test_get_success(self, application, server):
        now = datetime.now()
        transaction = {'description': 'Meal', 'amount': 300.0,
                       'type': transactions.INCOME_TRANSACTION,
                       'created_on': now}
        owner, expected = yield from self.prepare_data(
            application, transaction)

        expected['created_on'] = now.strftime('%d-%m-%Y %X')

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.get_transactions')
        }

        with (yield from server.response_ctx('GET', **params)) as resp:
            assert resp.status == 200

            response = yield from resp.json()
            assert 'transactions' in response
            assert [expected, ] == response['transactions']

    @async_test(create_database=True)
    def test_get_success_only_for_owner(self, application, server):
        transaction = {'description': 'Meal', 'amount': 300.0,
                       'type': transactions.INCOME_TRANSACTION}
        yield from self.prepare_data(application, transaction)

        another_owner = {'login': 'Samuel', 'password': 'top_secret'}
        yield from self.create_owner(application, another_owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(
                    another_owner))
            },
            'url': server.reverse_url('api.get_transactions')
        }

        with (yield from server.response_ctx('GET', **params)) as resp:
            assert resp.status == 200

            response = yield from resp.json()
            assert 'transactions' in response
            assert response['transactions'] == []

    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    @async_test(create_database=True)
    def test_create_unauthorized(self, application, server, headers):
        owner, account_id, category_id = yield from self.prepare_data(
            application)

        params = {
            'data': {'description': 'Meal', 'amount': 300.0,
                     'type': transactions.INCOME_TRANSACTION,
                     'account_id': account_id, 'category_id': category_id},
            'headers': headers,
            'url': server.reverse_url('api.create_transaction')
        }
        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 401

    @pytest.mark.parametrize('params', ({'json': False}, {'json': True}))
    @async_test(create_database=True)
    def test_create_success(self, application, server, params):
        owner, account_id, category_id = yield from self.prepare_data(
            application)
        token = yield from server.get_auth_token(owner)

        params['data'] = {'description': 'Meal', 'amount': 300.0,
                          'type': transactions.INCOME_TRANSACTION,
                          'account_id': account_id, 'category_id': category_id,
                          'created_on': '2015-08-20T00:00:00'}
        params['headers'] = {'X-ACCESS-TOKEN': token}
        params['url'] = server.reverse_url('api.create_transaction')

        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 201

            expected = {'id': 1, 'description': 'Meal', 'amount': 300.0,
                        'type': transactions.INCOME_TRANSACTION,
                        'account_id': account_id, 'category_id': category_id,
                        'created_on': '20-08-2015 00:00:00'}

            response = yield from response.json()
            assert 'transaction' in response
            assert expected == response['transaction']


class TestTransactionResource(BaseTransactionTest):

    @pytest.mark.parametrize('method,endpoint,headers', (
        ('GET', 'api.get_transaction', {}),
        ('GET', 'api.get_transaction', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('PUT', 'api.update_transaction', {}),
        ('PUT', 'api.update_transaction', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('DELETE', 'api.remove_transaction', {}),
        ('DELETE', 'api.remove_transaction', {'X-ACCESS-TOKEN': 'fake-token'})
    ))
    @async_test(create_database=True)
    def test_unauthorized(self, application, server, method, endpoint,
                          headers):
        transaction = {'description': 'Meal', 'amount': 300.0,
                       'type': transactions.EXPENSE_TRANSACTION}
        owner, expected = yield from self.prepare_data(
            application, transaction)

        params = {
            'headers': headers,
            'url': server.reverse_url(endpoint,
                                      {'instance_id': expected.get('id')})
        }
        with (yield from server.response_ctx(method, **params)) as response:
            assert response.status == 401

    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_transaction'),
        ('PUT', 'api.update_transaction'),
        ('DELETE', 'api.remove_transaction')
    ))
    @async_test(create_database=True)
    def test_does_not_belong(self, application, server, method, endpoint):
        transaction = {'description': 'Meal', 'amount': 300.0,
                       'type': transactions.INCOME_TRANSACTION}
        owner, expected = yield from self.prepare_data(
            application, transaction)

        another_owner = {'login': 'Sam', 'password': 'top_secret'}
        yield from self.create_owner(application, another_owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (
                    yield from server.get_auth_token(another_owner))
            },
            'url': server.reverse_url(endpoint,
                                      {'instance_id': expected.get('id')})
        }
        with (yield from server.response_ctx(method, **params)) as response:
            assert response.status == 404

    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_transaction'),
        ('PUT', 'api.update_transaction'),
        ('DELETE', 'api.remove_transaction'),
    ))
    @async_test(create_database=True)
    def test_missing(self, application, server, method, endpoint):
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

    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_transaction'),
        ('PUT', 'api.update_transaction'),
        ('DELETE', 'api.remove_transaction')
    ))
    @async_test(create_database=True)
    def test_wrong_instance_id(self, application, server, method, endpoint):
        owner = {'login': 'John', 'password': 'top_secret'}
        yield from self.create_owner(application, owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url(endpoint, {'instance_id': 'undefined'})
        }

        with (yield from server.response_ctx(method, **params)) as response:
            assert response.status == 400

    @async_test(create_database=True)
    def test_get_success(self, application, server):
        now = datetime.now()
        transaction = {'description': 'Meal', 'amount': 300.0,
                       'type': transactions.INCOME_TRANSACTION,
                       'created_on': now}
        owner, expected = yield from self.prepare_data(
            application, transaction)

        expected['created_on'] = now.strftime('%d-%m-%Y %X')

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.get_transaction',
                                      {'instance_id': expected.get('id')})
        }
        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 200

            data = yield from response.json()
            assert 'transaction' in data
            assert expected == data['transaction']

    @async_test(create_database=True)
    def test_update_success(self, application, server):
        now = datetime.now()
        transaction = {'description': 'Meal', 'amount': 300.0,
                       'type': transactions.INCOME_TRANSACTION,
                       'created_on': now}
        owner, expected = yield from self.prepare_data(
            application, transaction)

        expected['amount'] = 310.0
        params = {
            'data': {'amount': '310'},
            'json': True,
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.update_transaction',
                                      {'instance_id': expected.get('id')})
        }

        with (yield from server.response_ctx('PUT', **params)) as resp:
            assert resp.status == 200

            expected['created_on'] = now.strftime('%d-%m-%Y %X')
            response = yield from resp.json()
            assert 'transaction' in response
            assert expected == response['transaction']

    @async_test(create_database=True)
    def test_remove_success(self, application, server):
        transaction = {'description': 'Meal', 'amount': 300.0,
                       'type': transactions.INCOME_TRANSACTION,}
        owner, expected = yield from self.prepare_data(
            application, transaction)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.remove_transaction',
                                      {'instance_id': expected.get('id')})
        }
        with (yield from server.response_ctx('DELETE', **params)) as response:
            assert response.status == 200

        with (yield from application.engine) as conn:
            query = transactions.transactions_table.count().where(
                transactions.transactions_table.c.id == expected.get('id'))
            count = yield from conn.scalar(query)
            assert count == 0


class BaseTransactionDetailTest(BaseHandlerTest):

    @asyncio.coroutine
    def prepare_data(self, app):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(app, owner)

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': 0.0, 'owner_id': owner_id}
        account_id = yield from self.create_account(app, account)

        category = {'name': 'Food', 'owner_id': owner_id}
        category_id = yield from self.create_instance(
            app, categories.categories_table, category)

        transaction = {'description': 'Meal', 'amount': 300.0,
                       'type': transactions.INCOME_TRANSACTION,
                       'created_on': datetime.now(), 'account_id': account_id,
                       'category_id': category_id}
        transaction_id = yield from self.create_instance(
            app, transactions.transactions_table, transaction)

        return owner, transaction_id


class TestTransactionDetailsCollection(BaseTransactionDetailTest):

    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    @async_test(create_database=True)
    def test_get_unauthorized(self, application, server, headers):
        owner, transaction_id = yield from self.prepare_data(application)

        params = {
            'headers': headers,
            'url': server.reverse_url('api.get_details',
                                      {'transaction_id': transaction_id})
        }
        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 401

    @async_test(create_database=True)
    def test_get_success(self, application, server):
        owner, transaction_id = yield from self.prepare_data(application)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0, 'transaction_id': transaction_id}
        detail_id = yield from self.create_instance(
            application, transactions.transaction_details_table, detail)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.get_details',
                                      {'transaction_id': transaction_id})
        }

        with (yield from server.response_ctx('GET', **params)) as resp:
            assert resp.status == 200

            expected = {'id': detail_id, 'name': 'Soup',
                        'price_per_unit': 300.0, 'count': 1.0,
                        'transaction_id': transaction_id,
                        'total': 300.0}

            response = yield from resp.json()
            assert 'details' in response
            assert [expected, ] == response['details']

    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_details'),
        ('POST', 'api.create_detail')
    ))
    @async_test(create_database=True)
    def test_for_not_owner_transaction(self, application, server, method,
                                       endpoint):

        owner, transaction_id = yield from self.prepare_data(application)

        another_owner = {'login': 'Samuel', 'password': 'top_secret'}
        yield from self.create_owner(application, another_owner)
        token = yield from server.get_auth_token(another_owner)

        params = {
            'headers': {'X-ACCESS-TOKEN': token},
            'url': server.reverse_url(endpoint,
                                      {'transaction_id': transaction_id})
        }

        with (yield from server.response_ctx(method, **params)) as resp:
            assert resp.status == 403

    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_details'),
        ('POST', 'api.create_detail')
    ))
    @async_test(create_database=True)
    def test_for_missing_transaction(self, application, server, method,
                                     endpoint):

        owner, transaction_id = yield from self.prepare_data(application)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url(endpoint, {'transaction_id': 2})
        }
        with (yield from server.response_ctx(method, **params)) as resp:
            assert resp.status == 404

    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    @async_test(create_database=True)
    def test_create_unauthorized(self, application, server, headers):
        owner, transaction_id = yield from self.prepare_data(application)

        params = {
            'data': {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                     'total': 300.0, 'transaction_id': transaction_id},
            'headers': headers,
            'url': server.reverse_url('api.create_detail',
                                      {'transaction_id': transaction_id})
        }
        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 401

    @pytest.mark.parametrize('params', ({'json': True}, {'json': False}))
    @async_test(create_database=True)
    def test_create_success(self, application, server, params):
        owner, transaction_id = yield from self.prepare_data(application)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0}

        params['data'] = detail
        params['headers'] = {
            'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
        }
        params['url'] = server.reverse_url('api.create_detail',
                                           {'transaction_id': transaction_id})
        with (yield from server.response_ctx('POST', **params)) as resp:
            assert resp.status == 201

            expected = {'id': 1, 'name': 'Soup',
                        'transaction_id': transaction_id,
                        'price_per_unit': 300.0, 'count': 1.0, 'total': 300.0}

            response = yield from resp.json()
            assert 'detail' in response
            assert expected == response['detail']

    @pytest.mark.parametrize('params', ({'json': True}, {'json': False}))
    @async_test(create_database=True)
    def test_create_for_foreign(self, application, server, params):
        owner, transaction_id = yield from self.prepare_data(application)

        another_owner = {'login': 'Sam', 'password': 'top_secret'}
        yield from self.create_owner(application, another_owner)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0}

        params['data'] = detail
        params['headers'] = {
            'X-ACCESS-TOKEN': (yield from server.get_auth_token(another_owner))
        }
        params['url'] = server.reverse_url('api.create_detail',
                                           {'transaction_id': transaction_id})
        with (yield from server.response_ctx('POST', **params)) as resp:
            assert resp.status == 403


class TestTransactionDetailsResource(BaseTransactionDetailTest):

    @pytest.mark.parametrize('method,endpoint,headers', (
        ('GET', 'api.get_detail', {}),
        ('GET', 'api.get_detail', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('PUT', 'api.update_detail', {}),
        ('PUT', 'api.update_detail', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('DELETE', 'api.remove_detail', {}),
        ('DELETE', 'api.remove_detail', {'X-ACCESS-TOKEN': 'fake-token'})
    ))
    @async_test(create_database=True)
    def test_unauthorized(self, application, server, method, endpoint,
                          headers):
        owner, transaction_id = yield from self.prepare_data(application)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0, 'transaction_id': transaction_id}
        detail_id = yield from self.create_instance(
            application, transactions.transaction_details_table, detail)

        params = {
            'headers': headers,
            'url': server.reverse_url(endpoint, {
                'transaction_id': transaction_id, 'instance_id': detail_id
            })
        }
        with (yield from server.response_ctx(method, **params)) as response:
            assert response.status == 401

    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_detail'),
        ('PUT', 'api.update_detail'),
        ('DELETE', 'api.remove_detail')
    ))
    @async_test(create_database=True)
    def test_does_not_belong(self, application, server, method, endpoint):
        owner, transaction_id = yield from self.prepare_data(application)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0, 'transaction_id': transaction_id}
        detail_id = yield from self.create_instance(
            application, transactions.transaction_details_table, detail)

        another_owner = {'login': 'Sam', 'password': 'top_secret'}
        yield from self.create_owner(application, another_owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (
                    yield from server.get_auth_token(another_owner))
            },
            'url': server.reverse_url(endpoint, {
                'instance_id': detail_id, 'transaction_id': transaction_id
            })
        }
        with (yield from server.response_ctx(method, **params)) as response:
            assert response.status == 403

    @pytest.mark.parametrize('method,endpoint', (
        ('GET', 'api.get_detail'),
        ('PUT', 'api.update_detail'),
        ('DELETE', 'api.remove_detail')
    ))
    @async_test(create_database=True)
    def test_missing(self, application, server, method, endpoint):
        owner, transaction_id = yield from self.prepare_data(application)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url(endpoint, {
                'transaction_id': transaction_id, 'instance_id': 1
            })
        }
        with (yield from server.response_ctx(method, **params)) as response:
            assert response.status == 404

    @async_test(create_database=True)
    def test_get_success(self, application, server):
        owner, transaction_id = yield from self.prepare_data(application)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0, 'transaction_id': transaction_id}
        detail_id = yield from self.create_instance(
            application, transactions.transaction_details_table, detail)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.get_detail', {
                'transaction_id': transaction_id, 'instance_id': detail_id
            })
        }
        with (yield from server.response_ctx('GET', **params)) as resp:
            assert resp.status == 200

            detail['id'] = detail_id

            response = yield from resp.json()
            assert 'detail' in response
            assert detail == response['detail']

    @async_test(create_database=True)
    def test_update_success(self, application, server):
        owner, transaction_id = yield from self.prepare_data(application)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0, 'transaction_id': transaction_id}
        detail_id = yield from self.create_instance(
            application, transactions.transaction_details_table, detail)

        params = {
            'data': {'price_per_unit': 270.0},
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.update_detail', {
                'transaction_id': transaction_id, 'instance_id': detail_id
            })
        }

        detail['id'] = detail_id
        detail['price_per_unit'] = 270.0

        with (yield from server.response_ctx('PUT', **params)) as resp:
            assert resp.status == 200

            response = yield from resp.json()
            assert 'detail' in response
            assert detail == response['detail']

    @async_test(create_database=True)
    def test_remove_success(self, application, server):
        owner, transaction_id = yield from self.prepare_data(application)

        detail = {'name': 'Soup', 'price_per_unit': 300.0, 'count': 1.0,
                  'total': 300.0, 'transaction_id': transaction_id}
        detail_id = yield from self.create_instance(
            application, transactions.transaction_details_table, detail)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.remove_detail', {
                'transaction_id': transaction_id, 'instance_id': detail_id
            })
        }
        with (yield from server.response_ctx('DELETE', **params)) as resp:
            assert resp.status == 200

        with (yield from application.engine) as conn:
            query = transactions.transaction_details_table.count().where(
                transactions.transaction_details_table.c.id == detail.get('id'))
            count = yield from conn.scalar(query)
            assert count == 0
