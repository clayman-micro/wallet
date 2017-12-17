from datetime import datetime
from decimal import Decimal

import pytest

from wallet.entities import Account, EntityAlreadyExist, EntityNotFound, Owner
from wallet.repositories.accounts import AccountsRepository


@pytest.fixture(scope='module')
def user():
    return Owner('test@clayman.pro', pk=1)


@pytest.fixture(scope='module')
def factory():
    async def create(accounts, conn):
        query = """
            INSERT INTO accounts (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        for name, owner_id, enabled, created in accounts:
            await conn.execute(query, name, enabled, owner_id, created)
    return create


@pytest.mark.clean
@pytest.mark.parametrize('accounts,expected', (
    ((), 0),
    ((('Foo', False), ), 0),
    ((('Foo', True), ('Bar', False)), 1),
    ((('Foo', True), ('Bar', True)), 2),
))
async def test_fetch_accounts(client, user, factory, accounts, expected):
    async with client.server.app.db.acquire() as conn:
        now = datetime.now()
        await factory(map(
            lambda item: (item[0], user.pk, item[1], now), accounts
        ), conn)

        repo = AccountsRepository(conn=conn)
        accounts = await repo.fetch(owner=user)

    assert len(accounts) == expected


@pytest.mark.clean
@pytest.mark.parametrize('accounts,expected', (
    ((), 0),
    ((('Foo', False), ), 0),
    ((('Foo', True), ('Bar', False)), 1),
    ((('Foo', True), ('Bar', True)), 1),
    ((('Foo', True), ('Foe', True), ('Bar', True)), 2),
))
async def test_fetch_accounts_filter_by_name(client, user, factory, accounts,
                                             expected):
    async with client.server.app.db.acquire() as conn:
        now = datetime.now()

        await factory(map(
            lambda item: (item[0], user.pk, item[1], now), accounts
        ), conn)

        repo = AccountsRepository(conn=conn)
        accounts = await repo.fetch(owner=user, name='Fo')

    assert len(accounts) == expected


@pytest.mark.clean
async def test_fetch_account_by_pk_successed(client, user, factory):
    now = datetime.now()
    async with client.server.app.db.acquire() as conn:
        await factory((
            ('Foo', user.pk, True, now), ('Bar', user.pk, False, now)
        ), conn)

        repo = AccountsRepository(conn=conn)
        account = await repo.fetch_by_pk(owner=user, pk=1)

    assert isinstance(account, Account)
    assert account.pk == 1
    assert account.name == 'Foo'


@pytest.mark.clean
async def test_fetch_account_by_pk_failed(client, user, factory):
    async with client.server.app.db.acquire() as conn:
        repo = AccountsRepository(conn=conn)

        with pytest.raises(EntityNotFound):
            await repo.fetch_by_pk(owner=user, pk=1)


@pytest.mark.clean
async def test_save_account_successed(client, user):
    async with client.server.app.db.acquire() as conn:
        account = Account('Foo', Decimal(0.0), user, created_on=datetime.now())

        repo = AccountsRepository(conn=conn)
        pk = await repo.save(account)

    assert pk == 1


@pytest.mark.clean
async def test_save_account_failed(client, user, factory):
    async with client.server.app.db.acquire() as conn:
        now = datetime.now()

        await factory((
            ('Foo', user.pk, True, now), ('Bar', user.pk, False, now)
        ), conn)

        account = Account('Foo', Decimal(0.0), user)

        repo = AccountsRepository(conn=conn)
        with pytest.raises(EntityAlreadyExist):
            await repo.save(account)


@pytest.mark.clean
async def test_update_account_name_success(client, user):
    async with client.server.app.db.acquire() as conn:
        account = Account('Foo', Decimal(0.0), user)

        repo = AccountsRepository(conn=conn)
        account.pk = await repo.save(account)

        updated = await repo.update(account, name='Bar')

        acc = await repo.fetch_by_pk(user, account.pk)

    assert updated
    assert acc.name == 'Bar'


@pytest.mark.clean
async def test_update_account_amount(client, user):
    async with client.server.app.db.acquire() as conn:
        account = Account('Foo', Decimal(0.0), user)

        repo = AccountsRepository(conn=conn)
        account.pk = await repo.save(account)

        updated = await repo.update(account, amount=Decimal(100.0),
                                    original=Decimal(200.0))

        acc = await repo.fetch_by_pk(user, account.pk)

    assert updated
    assert acc.amount == Decimal(100.0)
    assert acc.original == Decimal(200.0)


@pytest.mark.clean
async def test_update_account_name_failed(client, user):
    async with client.server.app.db.acquire() as conn:
        account = Account('Foo', Decimal(0.0), user)
        another = Account('Bar', Decimal(100.0), user)

        repo = AccountsRepository(conn=conn)
        account.pk = await repo.save(account)
        another.pk = await repo.save(another)

        with pytest.raises(EntityAlreadyExist):
            await repo.update(account, name='Bar')


@pytest.mark.clean
async def test_remove_account_successed(client, user, factory):
    async with client.server.app.db.acquire() as conn:
        now = datetime.now()

        await factory((
            ('Foo', user.pk, True, now), ('Bar', user.pk, False, now)
        ), conn)

        account = Account('Foo', Decimal(0.0), user, pk=1)

        repo = AccountsRepository(conn=conn)
        removed = await repo.remove(account)

    assert removed


@pytest.mark.clean
async def test_remove_account_failed(client, user):
    async with client.server.app.db.acquire() as conn:
        account = Account('Foo', Decimal(0.0), user, pk=1)

        repo = AccountsRepository(conn=conn)
        removed = await repo.remove(account)

    assert not removed
