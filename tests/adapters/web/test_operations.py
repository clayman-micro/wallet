from decimal import Decimal

import pendulum  # type: ignore
import pytest  # type: ignore

from tests.adapters.web import assert_valid_response, prepare_payload
from tests.adapters.web.test_accounts import AccountMixin
from tests.storage import prepare_accounts, prepare_operations
from wallet.domain.entities import Account, Balance, Operation


operation_schema = {
    "type": "dict",
    "schema": {
        "id": {"required": True, "type": "integer"},
        "amount": {"required": True, "type": "float"},
        "type": {"required": True, "type": "string"},
        "description": {"required": True, "type": "string"},
        "created_on": {"required": True, "type": "string"},
        "account": {
            "required": True,
            "type": "dict",
            "schema": {"id": {"required": True, "type": "integer"}},
        },
    },
}


@pytest.fixture(scope="function")
def account(fake, user):
    now = pendulum.today()
    month = now.start_of("month")

    account = Account(
        key=0, name=fake.credit_card_number(), user=user, balance=[Balance(month=month.date())]
    )

    return account


class TestAddOperationToAccount(AccountMixin):
    @pytest.mark.integration
    @pytest.mark.parametrize("json", (True, False))
    async def test_unauthorized(self, aiohttp_client, app, passport, json, account):
        app["passport"] = passport
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])

        url = app.router.named_resources()["api.operations.add"].url_for(
            account_key=str(account.key)
        )
        payload, headers = prepare_payload({"amount": "100.0"}, json=json)
        resp = await client.post(url, data=payload, headers=headers)

        await assert_valid_response(resp, status=401)

    @pytest.mark.integration
    @pytest.mark.parametrize("json", (True, False))
    async def test_success(self, aiohttp_client, app, passport, json, account):
        app["passport"] = passport
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])

        url = app.router.named_resources()["api.operations.add"].url_for(
            account_key=str(account.key)
        )
        payload, headers = prepare_payload(
            {"amount": "100.0"}, {"X-ACCESS-TOKEN": "token"}, json=json
        )
        resp = await client.post(url, data=payload, headers=headers)

        await assert_valid_response(
            resp,
            status=201,
            content_type="application/json; charset=utf-8",
            schema={"operation": operation_schema},
        )


class TestFetchAccountOperations(AccountMixin):
    @pytest.mark.integration
    async def test_unauthorized(self, aiohttp_client, app, passport, account):
        app["passport"] = passport
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])

        url = app.router.named_resources()["api.operations.search"].url_for(
            account_key=str(account.key)
        )
        resp = await client.get(url)

        await assert_valid_response(resp, status=401)

    @pytest.mark.integration
    async def test_success(self, aiohttp_client, app, passport, account):
        app["passport"] = passport
        client = await aiohttp_client(app)

        operation = Operation(0, Decimal("838.0"), account, created_on=pendulum.today())

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])
            await prepare_operations(conn, [operation])

        url = app.router.named_resources()["api.operations.add"].url_for(
            account_key=str(account.key)
        )
        resp = await client.get(url, headers={"X-ACCESS-TOKEN": "token"})

        await assert_valid_response(
            resp,
            content_type="application/json; charset=utf-8",
            schema={"operations": {"required": True, "type": "list", "schema": operation_schema}},
        )


class TestFetchOperationFromAccount(AccountMixin):
    @pytest.mark.integration
    async def test_unauthorized(self, aiohttp_client, app, passport, account):
        app["passport"] = passport
        client = await aiohttp_client(app)

        operation = Operation(0, Decimal("838.0"), account, created_on=pendulum.today())

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])
            await prepare_operations(conn, [operation])

        url = app.router.named_resources()["api.operations.fetch"].url_for(
            account_key=str(account.key), operation_key=str(operation.key)
        )
        resp = await client.get(url)

        await assert_valid_response(resp, status=401)

    @pytest.mark.integration
    async def test_missing(self, aiohttp_client, app, passport, account):
        app["passport"] = passport
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])

        url = app.router.named_resources()["api.operations.fetch"].url_for(
            account_key=str(account.key), operation_key="1"
        )
        resp = await client.get(url, headers={"X-ACCESS-TOKEN": "token"})

        await assert_valid_response(resp, status=404)

    @pytest.mark.integration
    async def test_success(self, aiohttp_client, app, passport, account):
        app["passport"] = passport
        client = await aiohttp_client(app)

        operation = Operation(0, Decimal("838.0"), account, created_on=pendulum.today())

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])
            await prepare_operations(conn, [operation])

        url = app.router.named_resources()["api.operations.fetch"].url_for(
            account_key=str(account.key), operation_key=str(operation.key)
        )
        resp = await client.get(url, headers={"X-ACCESS-TOKEN": "token"})

        await assert_valid_response(
            resp,
            content_type="application/json; charset=utf-8",
            schema={"operation": operation_schema},
        )


class TestRemoveOperationFromAccount(AccountMixin):
    @pytest.mark.integration
    async def test_unauthorized(self, aiohttp_client, app, passport, account):
        app["passport"] = passport
        client = await aiohttp_client(app)

        operation = Operation(0, Decimal("838.0"), account, created_on=pendulum.today())

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])
            await prepare_operations(conn, [operation])

        url = app.router.named_resources()["api.operations.remove"].url_for(
            account_key=str(account.key), operation_key=str(operation.key)
        )
        resp = await client.delete(url)

        await assert_valid_response(resp, status=401)

    @pytest.mark.integration
    async def test_missing(self, aiohttp_client, app, passport, account):
        app["passport"] = passport
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])

        url = app.router.named_resources()["api.operations.remove"].url_for(
            account_key=str(account.key), operation_key="1"
        )
        resp = await client.delete(url, headers={"X-ACCESS-TOKEN": "token"})

        await assert_valid_response(resp, status=404)

    @pytest.mark.integration
    async def test_success(self, aiohttp_client, app, passport, account):
        app["passport"] = passport
        client = await aiohttp_client(app)

        operation = Operation(0, Decimal("838.0"), account, created_on=pendulum.today())

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])
            await prepare_operations(conn, [operation])

        url = app.router.named_resources()["api.operations.remove"].url_for(
            account_key=str(account.key), operation_key=str(operation.key)
        )
        resp = await client.delete(url, headers={"X-ACCESS-TOKEN": "token"})

        await assert_valid_response(resp, status=204)
