from datetime import datetime
from decimal import Decimal
from itertools import groupby
from typing import Dict, List

import sqlalchemy
from aiopg.sa import Engine, SAConnection
from dateutil.rrule import rrule, MONTHLY

from wallet import exceptions
from .base import create_table, get_instance
from .balance import table as balance_table


table = create_table('accounts', (
    sqlalchemy.Column('name', sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column('original_amount', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('owner_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('created_on', sqlalchemy.DateTime(), nullable=False)
))


async def get_accounts(owner: Dict, conn: SAConnection) -> Dict:
    accounts = {}

    params = table.c.owner_id == owner.get('id')

    async for row in conn.execute(sqlalchemy.select([table]).where(params)):
        account = dict(zip(row.keys(), row.values()))
        accounts[account['id']] = account

    total = await conn.scalar(
        sqlalchemy.select([sqlalchemy.func.count()]).select_from(
            table).where(params)
    )

    balance = []
    query = sqlalchemy.select([balance_table]).where(
        balance_table.c.account_id.in_(accounts.keys())).order_by(
        balance_table.c.date.desc())
    async for row in conn.execute(query):
        item = dict(zip(row.keys(), row.values()))
        balance.append(item)

    for key, group in groupby(balance, lambda b: b.get('account_id')):
        accounts[key]['balance'] = list(group)

    return accounts, total


async def get_account(instance_id, owner: Dict, conn: SAConnection) -> Dict:
    query = sqlalchemy.select([table]).where(sqlalchemy.and_(
        table.c.id == instance_id,
        table.c.owner_id == owner.get('id')
    ))
    account = await get_instance(query, conn=conn)

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


async def calculate_balance(account: Dict, until: datetime,
                            conn: SAConnection) -> List:
    query = '''
        SELECT
          SUM(transactions.amount),
          transactions.type,
          to_char(transactions.created_on, 'MM-YYYY') as date
        FROM transactions
        WHERE (
          transactions.account_id = {account_id}
        )
        GROUP BY transactions.type, transactions.created_on
        ORDER BY transactions.created_on ASC;
    '''.format(account_id=account.get('id'))

    total_by_month = {}

    min_date = until
    async for item in conn.execute(query):
        date = datetime.strptime(item.date, '%m-%Y')
        min_date = min(date, min_date)
        if item.date in total_by_month:
            total_by_month[item.date][item.type] = item.sum
        else:
            total_by_month[item.date] = {item.type: item.sum}

    if not total_by_month:
        t = min_date
        date = datetime(year=t.year, month=t.month, day=1)
        total_by_month[date.strftime('%m-%Y')] = {'income': 0, 'expense': 0}

    balance = []
    remain = account.get('original_amount', 0)
    if not isinstance(remain, Decimal):
        remain = Decimal(remain)
    for d in rrule(MONTHLY, dtstart=min_date, until=until):  # type: datetime
        key = d.strftime('%m-%Y')
        expense = Decimal(0)
        income = Decimal(0)
        if key in total_by_month:
            expense = total_by_month[key].get('expense', Decimal(0))
            income = total_by_month[key].get('income', Decimal(0))

        balance.append({
            'expense': expense, 'income': income, 'remain': remain, 'date': d
        })

        remain = remain + income - expense

    return balance
