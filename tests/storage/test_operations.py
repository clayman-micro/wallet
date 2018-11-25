from decimal import Decimal

import pendulum  # type: ignore
import pytest  # type: ignore

from wallet.domain.entities import Account, Operation, Tag
from wallet.domain.storage import OperationQuery
from wallet.storage.operations import OperationsDBRepo


@pytest.fixture(scope='function')
def account(fake, user):
    return Account(0, fake.credit_card_provider(), user)


async def prepare_operations(conn, operations):
    query = """
        INSERT INTO operations (
            amount, account_id, type, description, created_on
        ) VALUES ($1, $2, $3, $4, $5) RETURNING id;
    """

    for operation in operations:
        operation.key = await conn.fetchval(
            query, operation.amount, operation.account.key, operation.type.value,
            operation.description, operation.created_on
        )

    return operations


@pytest.mark.integration
async def test_add_operation(fake, app, account):
    now = pendulum.today()

    async with app['db'].acquire() as conn:
        account.key = await conn.fetchval("""
          INSERT INTO accounts (name, user_id, enabled, created_on)
          VALUES ($1, $2, $3, $4) RETURNING id;
        """, account.name, account.user.key, True, now)

        repo = OperationsDBRepo(conn)

        operation = Operation(0, Decimal('838.00'), account, created_on=now)
        key = await repo.add(operation)

        assert key == 1


@pytest.mark.integration
async def test_add_operation_with_tags(fake, app, user, account):
    now = pendulum.today()

    async with app['db'].acquire() as conn:
        account.key = await conn.fetchval("""
          INSERT INTO accounts (name, user_id, enabled, created_on)
          VALUES ($1, $2, $3, $4) RETURNING id;
        """, account.name, account.user.key, True, now)

        tag = Tag(0, fake.word(), user)
        tag.key = await conn.fetchval("""
          INSERT INTO tags (name, user_id, created_on)
          VALUES ($1, $2, $3) RETURNING id;
        """, tag.name, tag.user.key, now)

        repo = OperationsDBRepo(conn)

        operation = Operation(0, Decimal('838.0'), account, tags=[tag], created_on=now)
        key = await repo.add(operation)

        assert key == 1

        operation_tags = await conn.fetchval("""
            SELECT COUNT(*) FROM operation_tags WHERE operation_id = $1;
        """, key)

        assert operation_tags == 1


@pytest.mark.integration
async def test_find_operation_by_key(fake, app, account):
    now = pendulum.today()

    async with app['db'].acquire() as conn:
        account.key = await conn.fetchval("""
          INSERT INTO accounts (name, user_id, enabled, created_on)
          VALUES ($1, $2, $3, $4) RETURNING id;
        """, account.name, account.user.key, True, now)

        expected = await prepare_operations(conn, [
            Operation(0, Decimal('838.0'), account, created_on=now),
            Operation(0, Decimal('838.0'), account, created_on=now),
        ])

        repo = OperationsDBRepo(conn)

        query = OperationQuery(account=account, key=expected[0].key)
        operations = await repo.find(query)

        assert operations == [expected[0]]


@pytest.mark.integration
async def test_remove_operation(fake, app, account):
    now = pendulum.today()

    async with app['db'].acquire() as conn:
        account.key = await conn.fetchval("""
          INSERT INTO accounts (name, user_id, enabled, created_on)
          VALUES ($1, $2, $3, $4) RETURNING id;
        """, account.name, account.user.key, True, now)

        operations = await prepare_operations(conn, [
            Operation(0, Decimal('838.0'), account, created_on=now),
        ])

        repo = OperationsDBRepo(conn)

        operation = operations[0]
        result = await repo.remove(operation)

        assert result is True


@pytest.mark.integration
async def test_remove_operation_failed(fake, app, account):
    now = pendulum.today()

    async with app['db'].acquire() as conn:
        account.key = await conn.fetchval("""
          INSERT INTO accounts (name, user_id, enabled, created_on)
          VALUES ($1, $2, $3, $4) RETURNING id;
        """, account.name, account.user.key, True, now)

        operation = Operation(1, Decimal('838.0'), account, created_on=now)

        repo = OperationsDBRepo(conn)
        result = await repo.remove(operation)

        assert result is False
