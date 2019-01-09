from decimal import Decimal

import pendulum  # type: ignore
import pytest  # type: ignore

from tests.storage import prepare_accounts, prepare_operations, prepare_tags
from wallet.domain import EntityAlreadyExist
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


@pytest.mark.integration
async def test_add_tag_to_operation(fake, app, user, account):
    now = pendulum.today()
    operation = Operation(0, Decimal("838.0"), account, created_on=now)

    tag = Tag(0, fake.word(), user)

    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])
        await prepare_operations(conn, [operation])
        await prepare_tags(conn, [tag])

        repo = OperationsDBRepo(conn)
        result = await repo.add_tag(operation, tag)

        assert result is True

        query = "SELECT COUNT(*) FROM operation_tags WHERE operation_id = $1 AND tag_id = $2"
        count = await conn.fetchval(query, operation.key, tag.key)

    assert count == 1


@pytest.mark.integration
async def test_add_existed_tag_to_operation(fake, app, user, account):
    now = pendulum.today()
    operation = Operation(0, Decimal("838.0"), account, created_on=now)

    tag = Tag(0, fake.word(), user)

    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])
        await prepare_operations(conn, [operation])
        await prepare_tags(conn, [tag])

        await conn.execute("""
          INSERT INTO operation_tags (operation_id, tag_id) VALUES ($1, $2);
        """, operation.key, tag.key)

        with pytest.raises(EntityAlreadyExist):
            repo = OperationsDBRepo(conn)
            await repo.add_tag(operation, tag)


@pytest.mark.integration
async def test_remove_tag_from_operation(fake, app, user, account):
    now = pendulum.today()
    operation = Operation(0, Decimal("838.0"), account, created_on=now)

    tag = Tag(0, fake.word(), user)

    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])
        await prepare_operations(conn, [operation])
        await prepare_tags(conn, [tag])

        await conn.execute("""
          INSERT INTO operation_tags (operation_id, tag_id) VALUES ($1, $2);
        """, operation.key, tag.key)

        repo = OperationsDBRepo(conn)
        result = await repo.remove_tag(operation, tag)

        assert result is True

        query = "SELECT COUNT(*) FROM operation_tags WHERE operation_id = $1 AND tag_id = $2"
        count = await conn.fetchval(query, operation.key, tag.key)

    assert count == 0
