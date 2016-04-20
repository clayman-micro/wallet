from datetime import datetime
from typing import List, Dict

import sqlalchemy
from aiopg.sa import SAConnection

from .base import create_table


table = create_table('balance', (
    sqlalchemy.Column('account_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('accounts.id', ondelete='CASCADE')),
    sqlalchemy.Column('income', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('expense', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('remain', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('date', sqlalchemy.Date(), nullable=False)
))


async def update_balance(balance: List, account: Dict, conn: SAConnection):
    existed = {}
    query = sqlalchemy.select([table]).where(
        table.c.account_id == account.get('id')).order_by(table.c.date.asc())

    async for item in conn.execute(query):
        key = datetime.combine(item.date, datetime.min.time())
        existed[key] = {
            'id': item.id,
            'income': item.income,
            'expense': item.expense,
            'remain': item.remain,
            'date': item.date
        }

    for item in balance:
        if item['date'] in existed:
            query = sqlalchemy.update(table).where(
                table.c.id == existed[item['date']]['id']).values(**item)
        else:
            query = sqlalchemy.insert(table, values={
                'account_id': account['id'], **item
            })

        await conn.execute(query)
