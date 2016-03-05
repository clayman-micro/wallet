from datetime import datetime
from decimal import Decimal
from typing import Dict, List

import sqlalchemy
from aiopg.sa import Engine
from sqlalchemy.orm import Query

from .base import create_table, get_instance
from .balance import table as balance_table


table = create_table('accounts', (
    sqlalchemy.Column('name', sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column('original_amount', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('owner_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('created_on', sqlalchemy.DateTime(), nullable=False)
))


def get_account_query(params) -> Query:
    return sqlalchemy.select([
        table,
        balance_table.c.income,
        balance_table.c.expense,
        balance_table.c.remain
    ]).select_from(sqlalchemy.join(
        table, balance_table,
        table.c.id == balance_table.c.account_id)
    ).where(params).group_by(table.c.id, balance_table.c.income,
                             balance_table.c.expense, balance_table.c.remain)


async def get_account(instance_id, date, owner: Dict, engine: Engine) -> Dict:
    account = await get_instance(get_account_query(sqlalchemy.and_(
        table.c.id == instance_id,
        table.c.owner_id == owner.get('id'),
        sqlalchemy.extract('year', balance_table.c.date) == date.year,
        sqlalchemy.extract('month', balance_table.c.date) == date.month
    )), engine=engine)

    balance = {}
    for key in ['income', 'expense', 'remain']:
        balance[key] = account.pop(key)
    del account['max_1']

    account['balance'] = balance
    return account


async def calculate_balance(account: Dict, engine: Engine) -> List:
    query = '''
        SELECT
          SUM(transactions.amount),
          transactions.type,
          to_char(transactions.created_on, 'MM-YYYY') as date
        FROM transactions
        WHERE (
          transactions.account_id = {account_id}
        )
        GROUP BY transactions.type, date
        ORDER BY date ASC;
    '''.format(account_id=account.get('id'))

    total_by_month = {}
    async with engine.acquire() as conn:
        async for item in conn.execute(query):
            date = datetime.strptime(item.date, '%m-%Y')
            if date in total_by_month:
                total_by_month[date][item.type] = item.sum
            else:
                total_by_month[date] = {item.type: item.sum}

    if not total_by_month:
        today = datetime.today()
        total_by_month[today] = {'income': 0, 'expense': 0}

    balance = []
    remain = account.get('original_amount', 0)
    for key, items in sorted(total_by_month.items(), key=lambda k: k[0]):
        expense = items.get('expense', Decimal(0))
        income = items.get('income', Decimal(0))

        balance.append({
            'expense': expense,
            'income': income,
            'remain': remain,
            'date': key
        })

        remain = remain + income - expense

    return balance
