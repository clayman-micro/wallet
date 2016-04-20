from datetime import datetime, date
from decimal import Decimal

import pytest
import sqlalchemy

from wallet.storage import accounts, transactions, balance

from ..handlers import create_account, create_category, create_transaction


@pytest.mark.storage
@pytest.mark.run_loop
async def test_calculate_balance_for_new_account(app, owner):
    account = await create_account({'name': 'Card', 'original_amount': 300.0,
                                    'owner_id': owner['id']}, app=app)

    until = datetime(2016, 2, 1)
    async with app['engine'].acquire() as conn:
        result = await accounts.calculate_balance(account, until, conn)

    assert result == [
        {'date': datetime(2016, 2, 1), 'remain': Decimal(300),
         'expense': Decimal(0), 'income': Decimal(0)}
    ]


@pytest.mark.storage
@pytest.mark.run_loop
async def test_calculate_balance(app, owner):
    account = await create_account({'name': 'Card', 'original_amount': 300.0,
                                    'owner_id': owner['id']}, app=app)
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app=app)

    fixture = (
        {'type': transactions.EXPENSE_TRANSACTION, 'description': 'Meal',
         'amount': 300, 'created_on': datetime(2015, 8, 20)},
        {'type': transactions.INCOME_TRANSACTION, 'description': 'Bonus',
         'amount': 1000, 'created_on': datetime(2015, 8, 12)},
        {'type': transactions.EXPENSE_TRANSACTION, 'description': 'Meal',
         'amount': 500, 'created_on': datetime(2015, 9, 20)},
        {'type': transactions.INCOME_TRANSACTION, 'description': 'Meal',
         'amount': 10000, 'created_on': datetime(2015, 11, 20)},
        {'type': transactions.EXPENSE_TRANSACTION, 'description': 'Meal',
         'amount': 1000, 'created_on': datetime(2016, 1, 1)},
    )

    for item in fixture:
        item.update(account_id=account['id'], category_id=category['id'])
        await create_transaction(item, app=app)

    until = datetime(2016, 2, 1)
    async with app['engine'].acquire() as conn:
        balance = await accounts.calculate_balance(account, until, conn)

    assert balance == [
        {'date': datetime(2015, 8, 1), 'remain': Decimal(300),
         'expense': Decimal(300), 'income': Decimal(1000)},
        {'date': datetime(2015, 9, 1), 'remain': Decimal(1000),
         'expense': Decimal(500.0), 'income': Decimal('0')},
        {'date': datetime(2015, 10, 1), 'remain': Decimal(500),
         'expense': Decimal(0), 'income': Decimal(0.0)},
        {'date': datetime(2015, 11, 1), 'remain': Decimal(500),
         'expense': Decimal(0), 'income': Decimal(10000.0)},
        {'date': datetime(2015, 12, 1), 'remain': Decimal(10500.00),
         'expense': Decimal(0), 'income': Decimal(0)},
        {'date': datetime(2016, 1, 1), 'remain': Decimal(10500),
         'expense': Decimal(1000), 'income': Decimal(0)},
        {'date': datetime(2016, 2, 1), 'remain': Decimal(9500),
         'expense': Decimal(0), 'income': Decimal(0)}
    ]


@pytest.mark.storage
@pytest.mark.run_loop
async def test_update_balance_for_new_account(app, owner):
    account = await create_account({'name': 'Card', 'original_amount': 300.0,
                                    'owner_id': owner['id']}, app=app)
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app=app)

    fixture = (
        {'type': transactions.INCOME_TRANSACTION, 'description': 'Meal',
         'amount': 10000, 'created_on': datetime(2015, 11, 20)},
        {'type': transactions.EXPENSE_TRANSACTION, 'description': 'Meal',
         'amount': 1000, 'created_on': datetime(2016, 1, 1)},
    )

    for item in fixture:
        item.update(account_id=account['id'], category_id=category['id'])
        await create_transaction(item, app=app)

    until = datetime(2016, 2, 1)
    async with app['engine'].acquire() as conn:
        calculated = await accounts.calculate_balance(account, until, conn)

        await balance.update_balance(calculated, account, conn)

        query = sqlalchemy.select([balance.table]).where(
            balance.table.c.account_id == account.get('id')).order_by(
            balance.table.c.date.asc())

        existed = []
        async for item in conn.execute(query):
            existed.append({
                'id': item.id,
                'income': item.income,
                'expense': item.expense,
                'remain': item.remain,
                'date': item.date
            })

    assert existed == [
        {'id': 1, 'income': Decimal(10000), 'expense': Decimal(0),
         'remain': Decimal(300), 'date': date(2015, 11, 1)},
        {'id': 2, 'income': Decimal(0), 'expense': Decimal(0),
         'remain': Decimal(10300), 'date': date(2015, 12, 1)},
        {'id': 3, 'income': Decimal(0), 'expense': Decimal(1000),
         'remain': Decimal(10300), 'date': date(2016, 1, 1)},
        {'id': 4, 'income': Decimal(0), 'expense': Decimal(0),
         'remain': Decimal(9300), 'date': date(2016, 2, 1)}
    ]
