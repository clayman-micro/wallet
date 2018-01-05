from datetime import datetime
from decimal import Decimal

import pytest

from wallet.entities import Account, EntityAlreadyExist, EntityNotFound
from wallet.repositories.accounts import AccountsRepository


async def save_account(account, conn):
    query = """
            INSERT INTO accounts (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
    pk = await conn.fetchval(query, account.name, account.enabled,
                             account.owner.pk, account.created_on)
    return pk


@pytest.mark.repositories
@pytest.mark.parametrize('accounts,expected', (
    ((), 0),
    ((('Foo', False), ), 0),
    ((('Foo', True), ('Bar', False)), 1),
    ((('Foo', True), ('Bar', True)), 2),
))
async def test_fetch_accounts(client, owner, accounts, expected):
    now = datetime.now()

    async with client.server.app.db.acquire() as conn:
        for name, enabled in accounts:
            account = Account(name, Decimal(0.0), owner, enabled=enabled,
                              created_on=now)
            account.pk = await save_account(account, conn)

        repo = AccountsRepository(conn=conn)
        accounts = await repo.fetch(owner)

    assert len(accounts) == expected


@pytest.mark.repositories
@pytest.mark.parametrize('accounts,expected', (
    ((), 0),
    ((('Foo', False), ), 0),
    ((('Foo', True), ('Bar', False)), 1),
    ((('Foo', True), ('Bar', True)), 1),
    ((('Foo', True), ('Foe', True), ('Bar', True)), 2),
))
async def test_fetch_accounts_filter_by_name(client, owner, accounts, expected):
    now = datetime.now()
    async with client.server.app.db.acquire() as conn:
        for name, enabled in accounts:
            account = Account(name, Decimal(0.0), owner, enabled=enabled,
                              created_on=now)
            account.pk = await save_account(account, conn)

        repo = AccountsRepository(conn=conn)
        accounts = await repo.fetch(owner, name='Fo')

    assert len(accounts) == expected


@pytest.mark.repositories
async def test_fetch_account_by_pk_successed(client, owner):
    now = datetime.now()
    async with client.server.app.db.acquire() as conn:
        for name, enabled in (('Foo', True), ('Bar', False)):
            account = Account(name, Decimal(0.0), owner, enabled=enabled,
                              created_on=now)
            account.pk = await save_account(account, conn)

        repo = AccountsRepository(conn=conn)
        account = await repo.fetch_account(owner, 1)

    assert isinstance(account, Account)
    assert account.pk == 1
    assert account.name == 'Foo'


@pytest.mark.repositories
async def test_fetch_account_by_pk_failed(client, owner):
    async with client.server.app.db.acquire() as conn:
        repo = AccountsRepository(conn=conn)

        with pytest.raises(EntityNotFound):
            await repo.fetch_account(owner, 1)


@pytest.mark.repositories
async def test_save_account_successed(client, owner):
    async with client.server.app.db.acquire() as conn:
        account = Account('Foo', Decimal(0.0), owner, created_on=datetime.now())

        repo = AccountsRepository(conn=conn)
        pk = await repo.save(account)

    assert pk == 1


@pytest.mark.repositories
async def test_save_account_failed(client, owner):
    now = datetime.now()

    async with client.server.app.db.acquire() as conn:
        for name, enabled in (('Foo', True), ('Bar', False)):
            account = Account(name, Decimal(0.0), owner, enabled=enabled,
                              created_on=now)
            account.pk = await save_account(account, conn)

        account = Account('Foo', Decimal(0.0), owner)

        repo = AccountsRepository(conn=conn)
        with pytest.raises(EntityAlreadyExist):
            await repo.save(account)


@pytest.mark.repositories
@pytest.mark.parametrize('fields', (
    {'name': 'Bar'},
    {'original': Decimal(1000.0)},
    {'amount': Decimal(2000.0)}
))
async def test_update_account(client, owner, fields):
    now = datetime.now()

    async with client.server.app.db.acquire() as conn:
        account = Account('Foo', Decimal(0.0), owner, created_on=now)
        account.pk = await save_account(account, conn)

        for key, value in iter(fields.items()):
            setattr(account, key, value)

        repo = AccountsRepository(conn=conn)

        updated = await repo.update(account, list(fields.keys()))

    assert updated


@pytest.mark.repositories
async def test_update_account_name_failed(client, owner):
    now = datetime.now()

    async with client.server.app.db.acquire() as conn:
        for name, enabled in (('Foo', True), ('Bar', True)):
            account = Account(name, Decimal(0.0), owner, enabled=enabled,
                              created_on=now)
            account.pk = await save_account(account, conn)

        repo = AccountsRepository(conn=conn)
        account.name = 'Foo'

        with pytest.raises(EntityAlreadyExist):
            await repo.update(account, ('name', ))


@pytest.mark.repositories
@pytest.mark.parametrize('enabled,expected', (
    (True, True),
    (False, False),
))
async def test_remove_account(client, owner, enabled, expected):
    now = datetime.now()

    async with client.server.app.db.acquire() as conn:
        for name, enabled in (('Foo', enabled), ('Bar', enabled)):
            account = Account(name, Decimal(0.0), owner, enabled=enabled,
                              created_on=now)
            account.pk = await save_account(account, conn)

        repo = AccountsRepository(conn=conn)
        removed = await repo.remove(account)

    assert removed == expected
