from decimal import Decimal

import pendulum  # type: ignore
import pytest  # type: ignore

from tests.handlers import assert_valid_response, prepare_payload
from tests.storage import prepare_accounts, prepare_operations, prepare_tags
from wallet.domain import Operation


class TestAddOperationToAccount:
    @pytest.mark.integration
    @pytest.mark.parametrize("json", (True, False))
    async def test_unauthorized(self, aiohttp_client, app, json, account):
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
    async def test_success(self, aiohttp_client, app, json, token, account):
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])

        url = app.router.named_resources()["api.operations.add"].url_for(
            account_key=str(account.key)
        )
        payload, headers = prepare_payload(
            {"amount": "100.0"}, {"X-ACCESS-TOKEN": token}, json=json
        )
        resp = await client.post(url, data=payload, headers=headers)

        await assert_valid_response(
            resp, status=201, content_type="application/json; charset=utf-8"
        )


class TestFetchAccountOperations:
    @pytest.mark.integration
    async def test_unauthorized(self, aiohttp_client, app, account):
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])

        url = app.router.named_resources()["api.operations.search"].url_for(
            account_key=str(account.key)
        )
        resp = await client.get(url)

        await assert_valid_response(resp, status=401)

    @pytest.mark.integration
    async def test_success(
        self, aiohttp_client, app, token, account, operation, tag
    ):
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])
            await prepare_tags(conn, [tag])

            operation.tags = [tag]
            await prepare_operations(conn, [operation])

        url = app.router.named_resources()["api.operations.add"].url_for(
            account_key=str(account.key)
        )
        resp = await client.get(url, headers={"X-ACCESS-TOKEN": token})

        await assert_valid_response(
            resp, content_type="application/json; charset=utf-8",
        )


class TestFetchOperationFromAccount:
    @pytest.mark.integration
    async def test_unauthorized(self, aiohttp_client, app, account):
        client = await aiohttp_client(app)

        operation = Operation(
            0, Decimal("838.0"), account, created_on=pendulum.today()
        )

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])
            await prepare_operations(conn, [operation])

        url = app.router.named_resources()["api.operations.fetch"].url_for(
            account_key=str(account.key), operation_key=str(operation.key)
        )
        resp = await client.get(url)

        await assert_valid_response(resp, status=401)

    @pytest.mark.integration
    async def test_missing(self, aiohttp_client, app, token, account):
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])

        url = app.router.named_resources()["api.operations.fetch"].url_for(
            account_key=str(account.key), operation_key="1"
        )
        resp = await client.get(url, headers={"X-ACCESS-TOKEN": token})

        await assert_valid_response(resp, status=404)

    @pytest.mark.integration
    async def test_success(
        self, aiohttp_client, app, token, account, operation
    ):
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])
            await prepare_operations(conn, [operation])

        url = app.router.named_resources()["api.operations.fetch"].url_for(
            account_key=str(account.key), operation_key=str(operation.key)
        )
        resp = await client.get(url, headers={"X-ACCESS-TOKEN": token})

        await assert_valid_response(
            resp, content_type="application/json; charset=utf-8",
        )


class TestRemoveOperationFromAccount:
    @pytest.mark.integration
    async def test_unauthorized(self, aiohttp_client, app, account, operation):
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])
            await prepare_operations(conn, [operation])

        url = app.router.named_resources()["api.operations.remove"].url_for(
            account_key=str(account.key), operation_key=str(operation.key)
        )
        resp = await client.delete(url)

        await assert_valid_response(resp, status=401)

    @pytest.mark.integration
    async def test_missing(self, aiohttp_client, app, token, account):
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])

        url = app.router.named_resources()["api.operations.remove"].url_for(
            account_key=str(account.key), operation_key="1"
        )
        resp = await client.delete(url, headers={"X-ACCESS-TOKEN": token})

        await assert_valid_response(resp, status=404)

    @pytest.mark.integration
    async def test_success(
        self, aiohttp_client, app, token, account, operation
    ):
        client = await aiohttp_client(app)

        async with app["db"].acquire() as conn:
            await prepare_accounts(conn, [account])
            await prepare_operations(conn, [operation])

        url = app.router.named_resources()["api.operations.remove"].url_for(
            account_key=str(account.key), operation_key=str(operation.key)
        )
        resp = await client.delete(url, headers={"X-ACCESS-TOKEN": token})

        await assert_valid_response(resp, status=204)
