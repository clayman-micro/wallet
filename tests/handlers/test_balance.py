import pytest

from wallet.storage import accounts, transactions

from . import create_owner, create_account, create_category


class TestAccountBalance(object):
    owner = {'login': 'John', 'password': 'top_secret'}
    account = {'name': 'Credit card', 'original_amount': 30000.0,
               'current_amount': 30000.0}

    async def prepare_data(self, app, account):
        owner_id = await create_owner(app, self.owner)
        account['owner_id'] = owner_id
        account_id = await create_account(app, account)
        category_id = await create_category(app, {
            'name': 'Food', 'owner_id': owner_id
        })
        return owner_id, account_id, category_id

    async def create_transaction(self, client, token, transaction):
        params = {
            'json': True,
            'headers': {'X-ACCESS-TOKEN': token},
            'data': transaction,
            'endpoint': 'api.create_transaction'
        }
        async with client.request('POST', **params) as response:
            assert response.status == 201

            data = await response.json()
            transaction_id = data['transaction']['id']

        return transaction_id

    @pytest.mark.run_loop
    @pytest.mark.parametrize('tr_type,amount,expected', (
        (transactions.INCOME_TRANSACTION, 10000, 40000.0),
        (transactions.EXPENSE_TRANSACTION, 300, 29700.0),
    ))
    async def test_update_after_add_transaction(self, app, client, tr_type,
                                                amount, expected):
        owner_id, account_id, category_id = await self.prepare_data(
            app, self.account)

        token = await client.get_auth_token(self.owner)
        await self.create_transaction(client, token, {
            'description': 'Meal', 'amount': amount, 'type': tr_type,
            'account_id': account_id, 'category_id': category_id,
            'created_on': '2015-08-20T00:00:00'
        })

        async with app['engine'].acquire() as conn:
            query = accounts.table.select().where(
                accounts.table.c.id == account_id)
            result = await conn.execute(query)
            account = await result.fetchone()

            assert account.current_amount == expected

    @pytest.mark.run_loop
    @pytest.mark.parametrize('tr_type,before,after,expected', (
        (transactions.INCOME_TRANSACTION, 10000, 12000, 42000.0),
        (transactions.EXPENSE_TRANSACTION, 300, 400, 29600.0),
    ))
    async def test_update_after_update_transaction(self, app, client, tr_type,
                                                   before, after, expected):
        owner_id, account_id, category_id = await self.prepare_data(
            app, self.account)

        token = await client.get_auth_token(self.owner)
        transaction_id = await self.create_transaction(client, token, {
            'description': 'Meal', 'amount': before, 'type': tr_type,
            'account_id': account_id, 'category_id': category_id,
            'created_on': '2015-08-20T00:00:00'
        })

        params = {
            'json': True,
            'headers': {'X-ACCESS-TOKEN': token},
            'data': {'amount': after},
            'endpoint': 'api.update_transaction',
            'endpoint_params': {
                'instance_id': transaction_id
            }
        }
        async with client.request('PUT', **params) as response:
            assert response.status == 200

        async with app['engine'].acquire() as conn:
            query = accounts.table.select().where(
                accounts.table.c.id == account_id)
            result = await conn.execute(query)
            account = await result.fetchone()

            assert account.current_amount == expected

    @pytest.mark.run_loop
    @pytest.mark.parametrize('tr_type,amount', (
        (transactions.INCOME_TRANSACTION, 10000),
        (transactions.EXPENSE_TRANSACTION, 300),
    ))
    async def test_update_after_remove_transaction(self, app, client, tr_type,
                                                   amount):
        owner_id, account_id, category_id = await self.prepare_data(
            app, self.account)

        token = await client.get_auth_token(self.owner)
        transaction_id = await self.create_transaction(client, token, {
            'description': 'Meal', 'amount': amount, 'type': tr_type,
            'account_id': account_id, 'category_id': category_id,
            'created_on': '2015-08-20T00:00:00'
        })
        params = {
            'headers': {'X-ACCESS-TOKEN': token},
            'endpoint': 'api.remove_transaction',
            'endpoint_params': {'instance_id': transaction_id}
        }
        async with client.request('DELETE', **params) as response:
            assert response.status == 200

        async with app['engine'].acquire() as conn:
            query = accounts.table.select().where(
                accounts.table.c.id == account_id)
            result = await conn.execute(query)
            account = await result.fetchone()

            assert account.current_amount == self.account['current_amount']

    @pytest.mark.run_loop
    async def test_transaction_change_account(self, app, client):
        owner_id, account_id, category_id = await self.prepare_data(
            app, self.account)

        token = await client.get_auth_token(self.owner)

        transaction_id = await self.create_transaction(client, token, {
            'description': 'Meal', 'amount': 3000,
            'type': transactions.EXPENSE_TRANSACTION,
            'account_id': account_id, 'category_id': category_id,
            'created_on': '2015-08-20T00:00:00'
        })

        another_account = {'name': 'Debit card', 'original_amount': 10000.0,
                           'owner_id': owner_id}
        another_id = await create_account(app, another_account)

        params = {
            'json': True,
            'headers': {'X-ACCESS-TOKEN': token},
            'data': {'account_id': another_id},
            'endpoint': 'api.update_transaction',
            'endpoint_params': {
                'instance_id': transaction_id
            }
        }
        async with client.request('PUT', **params) as response:
            assert response.status == 200

        async with app['engine'].acquire() as conn:
            result = await conn.execute(accounts.table.select().where(
                accounts.table.c.id == account_id))
            account = await result.fetchone()

            assert account['original_amount'] == account['current_amount']

            result = await conn.execute(accounts.table.select().where(
                accounts.table.c.id == another_id))
            another = await result.fetchone()

            assert another['current_amount'] == 7000.0
