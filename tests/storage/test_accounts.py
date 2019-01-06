from decimal import Decimal

import pendulum  # type: ignore
import pytest  # type: ignore
# import ujson  # type: ignore

from tests.storage import prepare_accounts
from wallet.domain import EntityAlreadyExist
from wallet.domain.entities import Account, Balance
from wallet.domain.storage import AccountQuery
from wallet.storage.accounts import AccountsDBRepo


@pytest.mark.integration
async def test_add_account(fake, app, user):
    account = Account(0, fake.credit_card_provider(), user)

    async with app['db'].acquire() as conn:
        repo = AccountsDBRepo(conn)
        key = await repo.add(account)

        assert key == 1

        name = await conn.fetchval("""
          SELECT name FROM accounts
          WHERE enabled = True AND user_id = $1 AND id = $2;
        """, user.key, key)

        assert name == account.name

        balance_enties = await conn.fetchval("""
            SELECT COUNT(id) FROM balance WHERE account_id = $1
        """, key)

        assert balance_enties == 1


@pytest.mark.integration
async def test_add_account_failed(fake, app, user):
    now = pendulum.today()
    month = now.start_of('month')
    name = fake.credit_card_number()

    async with app['db'].acquire() as conn:
        await prepare_accounts(conn, [
            Account(key=0, name=name, user=user, balance=[
                Balance(rest=Decimal('-838.00'), expenses=Decimal('838.00'),
                        incomes=Decimal('0.00'), month=month.date())
            ]),
        ])

        with pytest.raises(EntityAlreadyExist):
            account = Account(0, name, user)

            repo = AccountsDBRepo(conn)
            await repo.add(account)


@pytest.mark.integration
async def test_find_account_by_key(fake, app, user):
    now = pendulum.today()
    month = now.start_of('month')

    async with app['db'].acquire() as conn:
        repo = AccountsDBRepo(conn)

        expected = await prepare_accounts(conn, [
            Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                Balance(rest=Decimal('-838.00'), expenses=Decimal('838.00'),
                        incomes=Decimal('0.00'), month=month.date())
            ]),
            Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                Balance(rest=Decimal('0.0'), expenses=Decimal('0.0'),
                        incomes=Decimal('0.0'), month=month.date())
            ])
        ])

        query = AccountQuery(user=user, key=expected[0].key)
        accounts = await repo.find(query)

        assert accounts == [expected[0]]


@pytest.mark.integration
async def test_find_account_by_name(fake, app, user):
    now = pendulum.today()
    month = now.start_of('month')

    async with app['db'].acquire() as conn:
        expected = await prepare_accounts(conn, [
            Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                Balance(rest=Decimal('-838.00'), expenses=Decimal('838.00'),
                        incomes=Decimal('0.00'), month=month.date())
            ]),
            Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                Balance(rest=Decimal('0.0'), expenses=Decimal('0.0'),
                        incomes=Decimal('0.0'), month=month.date())
            ])
        ])

        repo = AccountsDBRepo(conn)

        query = AccountQuery(user=user, name=expected[0].name)
        accounts = await repo.find(query)

        assert accounts == [expected[0]]


@pytest.mark.integration
async def test_update_account_name(fake, app, user):
    now = pendulum.today()
    month = now.start_of('month')

    async with app['db'].acquire() as conn:
        accounts = await prepare_accounts(conn, [
            Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                Balance(rest=Decimal('-838.00'), expenses=Decimal('838.00'),
                        incomes=Decimal('0.00'), month=month.date())
            ]),
            Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                Balance(rest=Decimal('0.0'), expenses=Decimal('0.0'),
                        incomes=Decimal('0.0'), month=month.date())
            ])
        ])

        account = accounts[0]
        account.name = fake.credit_card_number()

        repo = AccountsDBRepo(conn)
        result = await repo.update(accounts[0], fields=('name', ))

        assert result is True

        name = await conn.fetchval("""
            SELECT name FROM accounts
            WHERE enabled = TRUE AND user_id = $1 AND id = $2;
        """, user.key, account.key)

        assert name == account.name


@pytest.mark.integration
async def test_update_account_duplicate_name(fake, app, user):
    now = pendulum.today()
    month = now.start_of('month')

    async with app['db'].acquire() as conn:
        accounts = await prepare_accounts(conn, [
            Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                Balance(rest=Decimal('-838.00'), expenses=Decimal('838.00'),
                        incomes=Decimal('0.00'), month=month.date())
            ]),
            Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                Balance(rest=Decimal('0.0'), expenses=Decimal('0.0'),
                        incomes=Decimal('0.0'), month=month.date())
            ])
        ])

        account = accounts[0]
        account.name = accounts[1].name

        repo = AccountsDBRepo(conn)
        result = await repo.update(accounts[0], fields=('name', ))

        assert result is False


@pytest.mark.integration
async def test_update_account_name_failed(fake, app, user):
    async with app['db'].acquire() as conn:
        account = Account(key=0, name=fake.credit_card_number(), user=user)

        account.name = fake.credit_card_number()

        repo = AccountsDBRepo(conn)
        result = await repo.update(account, fields=('name', ))

        assert result is False


@pytest.mark.integration
async def test_update_balance_single_entry(fake, app, user):
    now = pendulum.today().date()
    month = now.start_of('month')

    async with app['db'].acquire() as conn:
        accounts = await prepare_accounts(conn, [
            Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                Balance(rest=Decimal('0.00'), expenses=Decimal('0.00'),
                        incomes=Decimal('0.00'), month=month)
            ])
        ])

        account = accounts[0]
        account.balance = [
            Balance(rest=Decimal('25000.00'), expenses=Decimal('0.00'),
                    incomes=Decimal('25000.00'), month=month)
        ]

        repo = AccountsDBRepo(conn)
        result = await repo.update(account, fields=('balance', ))

        assert result is True

        query = AccountQuery(user=user, key=account.key)
        accounts = await repo.find(query)

        assert accounts[0].balance == [
            Balance(rest=Decimal('25000.00'), expenses=Decimal('0.00'),
                    incomes=Decimal('25000.00'), month=month)
        ]


@pytest.mark.integration
async def test_update_balance_with_missing_entries(fake, app, user):
    now = pendulum.today().date()
    month = now.start_of('month')

    async with app['db'].acquire() as conn:
        accounts = await prepare_accounts(conn, [
            Account(key=0, name=fake.credit_card_number(), user=user, balance=[
                Balance(rest=Decimal('0.00'), expenses=Decimal('0.00'),
                        incomes=Decimal('0.00'), month=month)
            ])
        ])

        account = accounts[0]
        account.balance = [
            Balance(rest=Decimal('-838.00'), expenses=Decimal('838.00'),
                    incomes=Decimal('0.00'), month=month.subtract(months=1)),
            Balance(rest=Decimal('24162.00'), expenses=Decimal('0.00'),
                    incomes=Decimal('25000.00'), month=month)
        ]

        repo = AccountsDBRepo(conn)
        result = await repo.update(account, fields=('balance', ))

        assert result is True

        query = AccountQuery(user=user, key=account.key)
        accounts = await repo.find(query)

        assert accounts[0].balance == [
            Balance(rest=Decimal('24162.00'), expenses=Decimal('0.00'),
                    incomes=Decimal('25000.00'), month=month),
            Balance(rest=Decimal('-838.00'), expenses=Decimal('838.00'),
                    incomes=Decimal('0.00'), month=month.subtract(months=1))
        ]


@pytest.mark.integration
async def test_remove_account(fake, app, user):
    now = pendulum.today()
    month = now.start_of('month')
    name = fake.credit_card_number()

    async with app['db'].acquire() as conn:
        accounts = await prepare_accounts(conn, [
            Account(key=0, name=name, user=user, balance=[
                Balance(rest=Decimal('-838.00'), expenses=Decimal('838.00'),
                        incomes=Decimal('0.00'), month=month.date())
            ]),
        ])

        repo = AccountsDBRepo(conn)
        result = await repo.remove(accounts[0])

        assert result is True

        count = await conn.fetchval("""
            SELECT COUNT(id) FROM accounts WHERE enabled = TRUE AND user_id = $1;
        """, user.key)

        assert count == 0


@pytest.mark.integration
async def test_remove_account_failed(fake, app, user):
    async with app['db'].acquire() as conn:
        account = Account(key=0, name=fake.credit_card_number(), user=user)

        repo = AccountsDBRepo(conn)
        result = await repo.remove(account)

        assert result is False
