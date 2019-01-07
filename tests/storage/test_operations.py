from decimal import Decimal

import pendulum  # type: ignore
import pytest  # type: ignore

from tests.storage import prepare_accounts, prepare_operations, prepare_tags
from wallet.domain.entities import Account, Operation, Tag
from wallet.domain.storage import OperationQuery
from wallet.storage.operations import OperationsDBRepo


@pytest.fixture(scope="function")
def account(fake, user):
    return Account(0, fake.credit_card_provider(), user)


@pytest.mark.integration
async def test_add_operation(fake, app, account):
    now = pendulum.today()

    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])

        repo = OperationsDBRepo(conn)

        operation = Operation(0, Decimal("838.00"), account, created_on=now)
        key = await repo.add(operation)

        assert key == 1


@pytest.mark.integration
async def test_add_operation_with_tags(fake, app, user, account):
    now = pendulum.today()

    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])

        tag = Tag(0, fake.word(), user)
        await prepare_tags(conn, [tag])

        repo = OperationsDBRepo(conn)

        operation = Operation(0, Decimal("838.0"), account, tags=[tag], created_on=now)
        key = await repo.add(operation)

        assert key == 1

        query = "SELECT COUNT(*) FROM operation_tags WHERE operation_id = $1"
        operation_tags = await conn.fetchval(query, key)

        assert operation_tags == 1


@pytest.mark.integration
async def test_find_operation_by_key(fake, app, account):
    now = pendulum.today()

    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])

        expected = await prepare_operations(
            conn,
            [
                Operation(0, Decimal("838.0"), account, created_on=now),
                Operation(0, Decimal("838.0"), account, created_on=now),
            ],
        )

        repo = OperationsDBRepo(conn)

        query = OperationQuery(account=account, key=expected[0].key)
        operations = await repo.find(query)

        assert operations == [expected[0]]


@pytest.mark.integration
async def test_remove_operation(fake, app, account):
    now = pendulum.today()

    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])

        operations = await prepare_operations(
            conn, [Operation(0, Decimal("838.0"), account, created_on=now)]
        )

        repo = OperationsDBRepo(conn)

        operation = operations[0]
        result = await repo.remove(operation)

        assert result is True


@pytest.mark.integration
async def test_remove_operation_failed(fake, app, account):
    now = pendulum.today()

    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])

        operation = Operation(1, Decimal("838.0"), account, created_on=now)

        repo = OperationsDBRepo(conn)
        result = await repo.remove(operation)

        assert result is False
