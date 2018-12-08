from decimal import Decimal

import pendulum   # type: ignore
import pytest  # type: ignore
import ujson  # type: ignore

from wallet.domain.entities import Account, Balance
from wallet.validation import Validator


class AccountMixin:
    def prepare_request(self, data, headers=None, json=False):
        if headers is None:
            headers = {}

        if json:
            data = ujson.dumps(data)
            headers['Content-Type'] = 'application/json'

        return {'data': data, 'headers': headers}

    async def prepare_accounts(self, conn, accounts):
        now = pendulum.today()

        for account in accounts:
            account.key = await conn.fetchval("""
            INSERT INTO accounts (name, user_id, enabled, created_on)
            VALUES ($1, $2, $3, $4) RETURNING id;
            """, account.name, account.user.key, True, now)

            query = """
            INSERT INTO balance (rest, expenses, incomes, month, account_id)
            VALUES ($1, $2, $3, $4, $5);
            """
            await conn.executemany(query, [
                (item.rest, item.expenses, item.incomes, item.month, account.key)
                for item in account.balance
            ])

        return accounts


class TestRegisterAccount(AccountMixin):
    @pytest.mark.integration
    async def test_unauthorized(self, fake, aiohttp_client, app, passport):
        app['passport'] = passport
        client = await aiohttp_client(app)

        data = {'name': fake.credit_card_provider()}

        url = app.router.named_resources()['api.accounts.register'].url_for()
        resp = await client.post(url, **self.prepare_request(data, json=True))
        assert resp.status == 401

    @pytest.mark.integration
    async def test_success(self, fake, aiohttp_client, app, passport):
        app['passport'] = passport
        client = await aiohttp_client(app)

        data = {'name': fake.credit_card_provider()}

        url = app.router.named_resources()['api.accounts.register'].url_for()
        resp = await client.post(url, **self.prepare_request(data, {'X-ACCESS-TOKEN': 'token'}, True))

        assert resp.status == 201
        assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'

        validator = Validator(schema={
            'account': {'required': True, 'type': 'dict', 'schema': {
                'id': {'required': True, 'type': 'integer'},
                'name': {'required': True, 'type': 'string'},
                'balance': {'required': True, 'type': 'dict', 'schema': {
                    'incomes': {'required': True, 'type': 'float'},
                    'expenses': {'required': True, 'type': 'float'},
                    'rest': {'required': True, 'type': 'float'},
                }}
            }}
        })

        result = await resp.json()
        assert validator.validate_payload(result)


class TestSearchAccounts(AccountMixin):

    @pytest.mark.integration
    async def test_unauthorized(self, fake, aiohttp_client, app, passport):
        app['passport'] = passport
        client = await aiohttp_client(app)

        url = app.router.named_resources()['api.accounts'].url_for()
        resp = await client.get(url, headers={'Content-Type': 'application/json'})
        assert resp.status == 401

    @pytest.mark.integration
    async def test_success(self, fake, aiohttp_client, app, passport, user):
        app['passport'] = passport
        client = await aiohttp_client(app)

        async with app['db'].acquire() as conn:
            now = pendulum.today()
            month = now.start_of('month')

            await self.prepare_accounts(conn, [
                Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                    Balance(rest=Decimal('-838.00'), expenses=Decimal('838.00'),
                            incomes=Decimal('0.00'), month=month.date())
                ]),
                Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                    Balance(rest=Decimal('0.0'), expenses=Decimal('0.0'),
                            incomes=Decimal('0.0'), month=month.date())
                ])
            ])

        url = app.router.named_resources()['api.accounts'].url_for()
        resp = await client.get(url, headers={
            'Content-Type': 'application/json',
            'X-ACCESS-TOKEN': 'token'
        })

        assert resp.status == 200
        assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'

        validator = Validator(schema={
            'accounts': {'required': True, 'type': 'list', 'schema': {
                'type': 'dict', 'schema': {
                    'id': {'required': True, 'type': 'integer'},
                    'name': {'required': True, 'type': 'string'},
                    'balance': {'required': True, 'type': 'dict', 'schema': {
                        'incomes': {'required': True, 'type': 'float'},
                        'expenses': {'required': True, 'type': 'float'},
                        'rest': {'required': True, 'type': 'float'},
                    }}
                }
            }}
        })

        result = await resp.json()
        assert validator.validate_payload(result)


class TestUpdateAccount(AccountMixin):

    @pytest.mark.integration
    async def test_unauthorized(self, fake, aiohttp_client, app, passport):
        app['passport'] = passport
        client = await aiohttp_client(app)

        data = {'name': fake.credit_card_provider()}

        url = app.router.named_resources()['api.accounts.update'].url_for(account_key='1')
        resp = await client.put(url, **self.prepare_request(data, json=True))
        assert resp.status == 401

    @pytest.mark.integration
    async def test_missing(self, fake, aiohttp_client, app, passport):
        app['passport'] = passport
        client = await aiohttp_client(app)

        url = app.router.named_resources()['api.accounts.update'].url_for(account_key='1')
        resp = await client.delete(url, headers={'X-ACCESS-TOKEN': 'token'})
        assert resp.status == 404

    @pytest.mark.integration
    async def test_success(self, fake, aiohttp_client, app, passport, user):
        app['passport'] = passport
        client = await aiohttp_client(app)

        async with app['db'].acquire() as conn:
            now = pendulum.today()
            month = now.start_of('month')

            accounts = await self.prepare_accounts(conn, [
                Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                    Balance(rest=Decimal('-838.00'), expenses=Decimal('838.00'),
                            incomes=Decimal('0.00'), month=month.date())
                ]),
            ])

        data = {'name': fake.credit_card_provider()}

        url = app.router.named_resources()['api.accounts.update'].url_for(
            account_key=str(accounts[0].key)
        )
        resp = await client.put(url, **self.prepare_request(data, {'X-ACCESS-TOKEN': 'token'}, True))
        assert resp.status == 204


class TestRemoveAccount(AccountMixin):

    @pytest.mark.integration
    async def test_unauthorized(self, fake, aiohttp_client, app, passport):
        app['passport'] = passport
        client = await aiohttp_client(app)

        url = app.router.named_resources()['api.accounts.remove'].url_for(account_key='1')
        resp = await client.delete(url)
        assert resp.status == 401

    @pytest.mark.integration
    async def test_missing(self, fake, aiohttp_client, app, passport):
        app['passport'] = passport
        client = await aiohttp_client(app)

        url = app.router.named_resources()['api.accounts.remove'].url_for(account_key='1')
        resp = await client.delete(url, headers={'X-ACCESS-TOKEN': 'token'})
        assert resp.status == 404

    @pytest.mark.integration
    async def test_success(self, fake, aiohttp_client, app, passport, user):
        app['passport'] = passport
        client = await aiohttp_client(app)

        async with app['db'].acquire() as conn:
            now = pendulum.today()
            month = now.start_of('month')

            accounts = await self.prepare_accounts(conn, [
                Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                    Balance(rest=Decimal('-838.00'), expenses=Decimal('838.00'),
                            incomes=Decimal('0.00'), month=month.date())
                ]),
            ])

        url = app.router.named_resources()['api.accounts.remove'].url_for(
            account_key=str(accounts[0].key)
        )
        resp = await client.delete(url, headers={'X-ACCESS-TOKEN': 'token'})
        assert resp.status == 204
