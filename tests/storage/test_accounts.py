from decimal import Decimal

import pytest  # type: ignore

from tests.storage import prepare_accounts
from wallet.domain import Account, Balance
from wallet.domain.storage import EntityAlreadyExist, EntityNotFound
from wallet.storage.accounts import AccountsDBRepo


@pytest.fixture(scope="function")
def accounts(fake, month, user):
    return [
        Account(key=0, name=fake.credit_card_number(), user=user, balance=[
            Balance(rest=Decimal("-838.00"), expenses=Decimal("838.00"), month=month)
        ]),
        Account(key=0, name=fake.credit_card_number(), user=user, balance=[
            Balance(month=month)
        ])
    ]


@pytest.mark.integration
async def test_add_account(fake, app, user):
    account = Account(0, fake.credit_card_provider(), user)

    async with app["db"].acquire() as conn:
        repo = AccountsDBRepo(conn)
        key = await repo.add(account)

        assert key == 1

        name = await conn.fetchval("""
          SELECT name FROM accounts
          WHERE enabled = True AND user_id = $1 AND id = $2;
        """, user.key, key)

        assert name == account.name

        balance_entities = await conn.fetchval("""
          SELECT COUNT(id) FROM balance WHERE account_id = $1
        """, key)

        assert balance_entities == 1


@pytest.mark.integration
async def test_add_account_failed(fake, app, month, user, account):
    name = fake.credit_card_number()

    account.name = name
    account.balance = [
        Balance(rest=Decimal("-838.00"), expenses=Decimal("838.00"), month=month)
    ]

    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])

        with pytest.raises(EntityAlreadyExist):
            account = Account(key=0, name=name, user=user)

            repo = AccountsDBRepo(conn)
            await repo.add(account)


@pytest.mark.integration
async def test_find_account_by_key(app, user, accounts):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, accounts)

        repo = AccountsDBRepo(conn)
        result = await repo.find_by_key(user, key=accounts[0].key)

        assert result == accounts[0]


@pytest.mark.integration
async def test_find_account_by_key_missing(app, user):
    async with app["db"].acquire() as conn:
        with pytest.raises(EntityNotFound):
            repo = AccountsDBRepo(conn)
            await repo.find_by_key(user, key=1)


@pytest.mark.integration
async def test_find_account_by_name(app, user, accounts):
    async with app["db"].acquire() as conn:
        expected = await prepare_accounts(conn, accounts)

        repo = AccountsDBRepo(conn)
        result = await repo.find_by_name(user, name=expected[0].name)

        assert result == [expected[0]]


@pytest.mark.integration
async def test_update_account_name(fake, app, user, accounts):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, accounts)

        account = accounts[0]
        account.name = fake.credit_card_number()

        repo = AccountsDBRepo(conn)
        result = await repo.update(account, fields=("name",))

        assert result is True

        name = await conn.fetchval("""
          SELECT name FROM accounts
          WHERE enabled = TRUE AND user_id = $1 AND id = $2;
        """, user.key, account.key)

        assert name == account.name


@pytest.mark.integration
async def test_update_account_duplicate_name(app, user, accounts):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, accounts)

        account = accounts[0]
        account.name = accounts[1].name

        repo = AccountsDBRepo(conn)
        result = await repo.update(accounts[0], fields=("name",))

        assert result is False


@pytest.mark.integration
async def test_update_account_name_failed(fake, app, user, account):
    async with app["db"].acquire() as conn:
        account.name = fake.credit_card_number()

        repo = AccountsDBRepo(conn)
        result = await repo.update(account, fields=("name",))

        assert result is False


@pytest.mark.integration
async def test_update_balance_single_entry(app, month, user, account):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])

        account.balance = [
            Balance(rest=Decimal("25000.00"), incomes=Decimal("25000.00"), month=month)
        ]

        repo = AccountsDBRepo(conn)
        result = await repo.update(account, fields=("balance",))

        assert result is True

        result = await repo.find_by_key(user, key=account.key)
        assert result.balance == [
            Balance(rest=Decimal("25000.00"), incomes=Decimal("25000.00"), month=month)
        ]


@pytest.mark.integration
async def test_update_balance_with_missing_entries(app, month, user, account):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])

        account.balance = [
            Balance(rest=Decimal("-838.00"), expenses=Decimal("838.00"), month=month.subtract(months=1)),
            Balance(rest=Decimal("24162.00"), incomes=Decimal("25000.00"), month=month),
        ]

        repo = AccountsDBRepo(conn)
        result = await repo.update(account, fields=("balance",))

        assert result is True

        result = await repo.find_by_key(user, key=account.key)
        assert result.balance == [
            Balance(rest=Decimal("24162.00"), incomes=Decimal("25000.00"), month=month),
            Balance(rest=Decimal("-838.00"), expenses=Decimal("838.00"), month=month.subtract(months=1)),
        ]


@pytest.mark.integration
async def test_remove_account(app, user, account):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])

        repo = AccountsDBRepo(conn)
        result = await repo.remove(account)

        assert result is True

        count = await conn.fetchval("""
          SELECT COUNT(id) FROM accounts WHERE enabled = TRUE AND user_id = $1;
        """, user.key)
        assert count == 0


@pytest.mark.integration
async def test_remove_account_failed(app, account):
    async with app["db"].acquire() as conn:
        repo = AccountsDBRepo(conn)
        result = await repo.remove(account)

        assert result is False
