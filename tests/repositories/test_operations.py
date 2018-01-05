from datetime import datetime
from decimal import Decimal

import pytest

from wallet.entities import EntityNotFound, Operation, OperationType
from wallet.repositories.operations import OperationsRepo


async def save_account(account, conn):
    query = """
            INSERT INTO accounts (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
    pk = await conn.fetchval(query, account.name, account.enabled,
                             account.owner.pk, account.created_on)
    return pk


async def save_operation(operation, conn):
    query = """
        INSERT INTO operations (
            type, amount, account_id, enabled,
            owner_id, created_on
        )
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id
    """
    pk = await conn.fetchval(query, operation.type.value.lower(),
                             operation.amount, operation.account.pk,
                             operation.enabled, operation.account.owner.pk,
                             operation.created_on)
    return pk


@pytest.mark.repositories
@pytest.mark.parametrize('operations,expected', (
    ((), 0),
    ((
        (OperationType.EXPENSE, Decimal(145.50), 'Meal', True),
        (OperationType.INCOME, Decimal(27000.00), 'Salary', True),
        (OperationType.EXPENSE, Decimal(227.00), 'Taxi', True),
        (OperationType.EXPENSE, Decimal(145.50), 'Meal', False),
    ), 3)
))
async def test_fetch_operations(client, owner, account, operations, expected):
    now = datetime.now()

    async with client.server.app.db.acquire() as conn:
        account.pk = await save_account(account, conn)

        for operation_type, amount, description, enabled in operations:
            operation = Operation(amount, account, enabled=enabled,
                                  type=operation_type, description=description,
                                  created_on=now)
            operation.pk = await save_operation(operation, conn)

        repo = OperationsRepo(conn=conn)
        operations = await repo.fetch(account, now.year, now.month)

    assert len(operations) == expected


@pytest.mark.repositories
async def test_fetch_operation_successed(client, owner, account):
    now = datetime.now()

    async with client.server.app.db.acquire() as conn:
        account.pk = await save_account(account, conn)

        expected = Operation(Decimal(145.00), account, created_on=now)
        expected.pk = await save_operation(expected, conn)

        repo = OperationsRepo(conn=conn)
        operation = await repo.fetch_operation(account, expected.pk)

    assert isinstance(operation, Operation)
    assert operation.pk == expected.pk
    assert operation.amount == expected.amount
    assert operation.type == expected.type
    assert operation.enabled == expected.enabled
    assert operation.created_on == expected.created_on


@pytest.mark.repositories
async def test_fetch_operation_failed(client, owner, account):
    async with client.server.app.db.acquire() as conn:
        account.pk = await save_account(account, conn)

        repo = OperationsRepo(conn=conn)
        with pytest.raises(EntityNotFound):
            await repo.fetch_operation(account, 1)


@pytest.mark.repositories
async def test_save_operation(client, owner, account):
    now = datetime.now()

    operation = Operation(Decimal(156.00), account, created_on=now)

    async with client.server.app.db.acquire() as conn:
        account.pk = await save_account(account, conn)

        repo = OperationsRepo(conn=conn)
        pk = await repo.save(operation)

    assert pk == 1


@pytest.mark.repositories
@pytest.mark.parametrize('fields', (
    {'type': OperationType.INCOME},
    {'amount': Decimal(200.0)},
    {'description': 'Taxi'},
    {'created_on': datetime(2018, 1, 1)},
))
async def test_update_operation_success(client, owner, account, fields):
    now = datetime.now()

    async with client.server.app.db.acquire() as conn:
        account.pk = await save_account(account, conn)

        operation = Operation(Decimal(145.00), account, created_on=now)
        operation.pk = await save_operation(operation, conn)

        for key, value in iter(fields.items()):
            setattr(operation, key, value)

        repo = OperationsRepo(conn=conn)
        updated = await repo.update(operation, list(fields.keys()))

    assert updated


@pytest.mark.repositories
@pytest.mark.parametrize('fields', (
    {'type': OperationType.INCOME},
    {'amount': Decimal(200.0)},
    {'description': 'Taxi'},
    {'created_on': datetime(2018, 1, 1)},
))
async def test_update_removed_operation(client, owner, account, fields):
    now = datetime.now()

    async with client.server.app.db.acquire() as conn:
        account.pk = await save_account(account, conn)

        operation = Operation(Decimal(145.00), account, enabled=False,
                              created_on=now)
        operation.pk = await save_operation(operation, conn)

        for key, value in iter(fields.items()):
            setattr(operation, key, value)

        repo = OperationsRepo(conn=conn)
        updated = await repo.update(operation, list(fields.keys()))

    assert not updated


@pytest.mark.repositories
@pytest.mark.parametrize('enabled,expected', (
    (True, True),
    (False, False),
))
async def test_remove_operation(client, owner, account, enabled, expected):
    now = datetime.now()

    async with client.server.app.db.acquire() as conn:
        account.pk = await save_account(account, conn)

        operation = Operation(Decimal(145.00), account, enabled=enabled,
                              created_on=now)
        operation.pk = await save_operation(operation, conn)

        repo = OperationsRepo(conn=conn)
        removed = await repo.remove(operation)

    assert removed == expected
