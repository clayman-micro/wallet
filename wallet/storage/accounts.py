from datetime import datetime
from decimal import Decimal
from itertools import groupby
from typing import Dict, List

import sqlalchemy
from aiopg.sa import Engine

from wallet import exceptions
from .base import create_table
from .balance import table as balance_table


table = create_table('accounts', (
    sqlalchemy.Column('name', sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column('original_amount', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('owner_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('created_on', sqlalchemy.DateTime(), nullable=False)
))


async def get_accounts(owner: Dict, engine: Engine) -> Dict:
    accounts = {}

    params = table.c.owner_id == owner.get('id')
    async with engine.acquire() as conn:
        query = sqlalchemy.select([table]).where(params)
        async for row in conn.execute(query):
            account = dict(zip(row.keys(), row.values()))
            accounts[account['id']] = account

        total = await conn.scalar(
            sqlalchemy.select([sqlalchemy.func.count()])
                .select_from(table)
                .where(params)
        )

        balance = []
        query = sqlalchemy.select([balance_table]).where(
            balance_table.c.account_id.in_(accounts.keys())).order_by(
            balance_table.c.date.desc())
        async for row in conn.execute(query):
            item = dict(zip(row.keys(), row.values()))
            balance.append(item)

        for key, group in groupby(balance, lambda item: item.get('account_id')):
            accounts[key]['balance'] = list(group)

    return accounts, total


async def get_account(instance_id, owner: Dict, engine: Engine) -> Dict:
    async with engine.acquire() as conn:
        query = sqlalchemy.select([table]).where(sqlalchemy.and_(
            table.c.id == instance_id,
            table.c.owner_id == owner.get('id')
        ))
        result = await conn.execute(query)
        if not result.returns_rows:
            raise exceptions.ResourceNotFound
        row = await result.fetchone()

        account = dict(zip(row.keys(), row.values()))
        balance = {'income': 0, 'expense': 0,
                   'remain': account.get('original_amount')}

        query = sqlalchemy.select([balance_table]).where(
            balance_table.c.account_id == account.get('id')
        ).order_by(balance_table.c.date.desc())

        result = await conn.execute(query)
        if result.returns_rows and result.rowcount:
            row = await result.fetchone()
            balance = {
                'income': row.income,
                'expense': row.expense,
                'remain': row.remain
            }

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
