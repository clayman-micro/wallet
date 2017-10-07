from datetime import datetime

import pytest

from wallet import App  # noqa
from wallet.storage import AlreadyExist, ResourceNotFound
from wallet.storage.accounts import Account, AccountsRepo
from wallet.storage.owner import Owner


@pytest.fixture(scope='module')
def user():
    return Owner(1, 'foo@bar.baz')


@pytest.mark.storage
@pytest.mark.parametrize('accounts,expected', (
    ((), 0),
    ((('Foo', False), ), 0),
    ((('Foo', True), ('Bar', False)), 1),
    ((('Foo', True), ('Bar', True)), 2),
))
async def test_fetch_accounts(client, user, accounts, expected):
    app: App = client.server.app

    async with app.db.acquire() as conn:
        now = datetime.now()
        query = """
            INSERT INTO accounts (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        for name, enabled in accounts:
            await conn.execute(query, name, enabled, user.id, now)

    async with app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        accounts = await repo.fetch_many(owner=user)

    assert len(accounts) == expected


@pytest.mark.storage
async def test_fetch_account_succesed(client, user):
    app: App = client.server.app

    now = datetime.now()
    async with app.db.acquire() as conn:
        query = """
            INSERT INTO accounts (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        for name, enabled in (('Foo', True), ('Bar', False)):
            await conn.execute(query, name, enabled, user.id, now)

    async with app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        account = await repo.fetch(user, 1)

    assert isinstance(account, Account)
    assert account.id == 1
    assert account.name == 'Foo'


@pytest.mark.storage
async def test_fetch_tag_failed(client, user):
    async with client.server.app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)

        with pytest.raises(ResourceNotFound):
            await repo.fetch(user, 1)


@pytest.mark.storage
async def test_create_account_success(client, user):
    async with client.server.app.db.acquire() as conn:
        repo = AccountsRepo(conn=conn)
        account = await repo.create('Foo', user, created_on=datetime.now())

    assert isinstance(account, Account)
    assert account.id == 1
    assert account.name == 'Foo'
    assert account.amount == 0.0
    assert account.original == 0.0


@pytest.mark.storage
async def test_create_account_failed(client, user):
    async with client.server.app.db.acquire() as conn:
        now = datetime.now()
        query = """
            INSERT INTO accounts (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        await conn.execute(query, 'Foo', True, user.id, now)

        repo = AccountsRepo(conn=conn)

        with pytest.raises(AlreadyExist):
            await repo.create('Foo', user, created_on=now)


@pytest.mark.storage
@pytest.mark.parametrize('accounts', (
    (('Foo', True), ),
    (('Foo', True), ('Bar', False))
))
async def test_rename_account_success(client, user, accounts):
    async with client.server.app.db.acquire() as conn:
        now = datetime.now()

        query = """
            INSERT INTO accounts (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id;
        """

        created = []
        for name, enabled in accounts:
            account = Account(name, user, enabled=enabled)
            account.id = await conn.fetchval(
                query, account.name, account.enabled, account.owner_id, now
            )
            created.append(account)

        repo = AccountsRepo(conn=conn)
        success = await repo.rename(created[0], 'Bar')
        assert success

        query = 'SELECT name from accounts WHERE id = $1 AND owner_id = $2'
        account_name = await conn.fetchval(query, created[0].id, 1)
        assert account_name == 'Bar'


@pytest.mark.storage
async def test_rename_account_failed(client, user):
    async with client.server.app.db.acquire() as conn:
        now = datetime.now()

        query = """
            INSERT INTO accounts (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id;
        """
        for name, enabled in (('Foo', True), ('Bar', True)):
            await conn.execute(query, name, enabled, user.id, now)

        with pytest.raises(AlreadyExist):
            account = Account('Foo', user, id=1)

            repo = AccountsRepo(conn=conn)
            await repo.rename(account, 'Bar')


@pytest.mark.storage
@pytest.mark.parametrize('accounts,expected', (
    ((('Foo', True), ('Bar', True)), True),
    ((('Foo', False), ('Bar', True)), False),
))
async def test_remove_account_success(client, user, accounts, expected):
    now = datetime.now()

    async with client.server.app.db.acquire() as conn:
        query = """
            INSERT INTO accounts (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        created = []
        for name, enabled in accounts:
            account = Account(name, user, enabled=enabled)
            account.id = await conn.fetchval(
                query, account.name, account.enabled, account.owner_id, now
            )
            created.append(account)

        repo = AccountsRepo(conn=conn)
        removed = await repo.remove(created[0])
        assert removed == expected

        query = 'SELECT COUNT(id) from accounts WHERE id = $1 AND owner_id = $2 AND enabled = TRUE'  # noqa
        count = await conn.fetchval(query, created[0].id, 1)
        assert count == 0
