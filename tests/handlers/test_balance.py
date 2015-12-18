import asyncio
import pytest

from wallet.models import accounts, categories, transactions

from tests.conftest import async_test
from . import BaseHandlerTest


class TestAccountBalance(BaseHandlerTest):
    owner = {'login': 'John', 'password': 'top_secret'}
    account = {'name': 'Credit card', 'original_amount': 30000.0,
               'current_amount': 30000.0}

    @asyncio.coroutine
    def prepare_data(self, app, account):
        owner_id = yield from self.create_owner(app, self.owner)

        account['owner_id'] = owner_id
        account_id = yield from self.create_account(app, account)

        category_id = yield from self.create_instance(
            app, categories.categories_table, {
                'name': 'Food', 'owner_id': owner_id
            })

        return owner_id, account_id, category_id

    @asyncio.coroutine
    def create_transaction(self, server, token, transaction):
        params = {
            'json': True,
            'headers': {'X-ACCESS-TOKEN': token},
            'data': transaction,
            'url': server.reverse_url('api.create_transaction')
        }
        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 201

            data = yield from response.json()
            transaction_id = data['transaction']['id']

        return transaction_id

    @pytest.mark.parametrize('tr_type,amount,expected', (
        (transactions.INCOME_TRANSACTION, 10000, 40000.0),
        (transactions.EXPENSE_TRANSACTION, 300, 29700.0),
    ))
    @async_test(create_database=True)
    def test_update_after_add_transaction(self, application, server,
                                          tr_type, amount, expected):
        owner_id, account_id, category_id = yield from self.prepare_data(
            application, self.account)

        token = yield from server.get_auth_token(self.owner)
        yield from self.create_transaction(server, token, {
            'description': 'Meal', 'amount': amount, 'type': tr_type,
            'account_id': account_id, 'category_id': category_id,
            'created_on': '2015-08-20T00:00:00'
        })

        with (yield from application['engine']) as conn:
            query = accounts.accounts_table.select().where(
                accounts.accounts_table.c.id == account_id)
            result = yield from conn.execute(query)
            account = yield from result.fetchone()

            assert account.current_amount == expected

    @pytest.mark.parametrize('tr_type,before,after,expected', (
        (transactions.INCOME_TRANSACTION, 10000, 12000, 42000.0),
        (transactions.EXPENSE_TRANSACTION, 300, 400, 29600.0),
    ))
    @async_test(create_database=True)
    def test_update_after_update_transaction(self, application, server,
                                             tr_type, before, after, expected):
        owner_id, account_id, category_id = yield from self.prepare_data(
            application, self.account
        )

        token = yield from server.get_auth_token(self.owner)
        transaction_id = yield from self.create_transaction(server, token, {
            'description': 'Meal', 'amount': before, 'type': tr_type,
            'account_id': account_id, 'category_id': category_id,
            'created_on': '2015-08-20T00:00:00'
        })

        params = {
            'json': True,
            'headers': {'X-ACCESS-TOKEN': token},
            'data': {'amount': after},
            'url': server.reverse_url('api.update_transaction', parts={
                'instance_id': transaction_id})

        }
        with (yield from server.response_ctx('PUT', **params)) as response:
            assert response.status == 200

        with (yield from application['engine']) as conn:
            query = accounts.accounts_table.select().where(
                accounts.accounts_table.c.id == account_id)
            result = yield from conn.execute(query)
            account = yield from result.fetchone()

            assert account.current_amount == expected

    @pytest.mark.parametrize('tr_type,amount', (
        (transactions.INCOME_TRANSACTION, 10000),
        (transactions.EXPENSE_TRANSACTION, 300),
    ))
    @async_test(create_database=True)
    def test_update_after_remove_transaction(self, application, server,
                                             tr_type, amount):
        owner_id, account_id, category_id = yield from self.prepare_data(
            application, self.account
        )

        token = yield from server.get_auth_token(self.owner)
        transaction_id = yield from self.create_transaction(server, token, {
            'description': 'Meal', 'amount': amount, 'type': tr_type,
            'account_id': account_id, 'category_id': category_id,
            'created_on': '2015-08-20T00:00:00'
        })
        params = {
            'headers': {'X-ACCESS-TOKEN': token},
            'url': server.reverse_url('api.remove_transaction', parts={
                'instance_id': transaction_id})
        }
        with (yield from server.response_ctx('DELETE', **params)) as response:
            assert response.status == 200

        with (yield from application['engine']) as conn:
            query = accounts.accounts_table.select().where(
                accounts.accounts_table.c.id == account_id)
            result = yield from conn.execute(query)
            account = yield from result.fetchone()

            assert account.current_amount == self.account['current_amount']
