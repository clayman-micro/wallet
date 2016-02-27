from typing import List, Dict

import sqlalchemy
from aiopg.sa import Engine

from .base import create_table


table = create_table('balance', (
    sqlalchemy.Column('account_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('accounts.id', ondelete='CASCADE')),
    sqlalchemy.Column('income', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('expense', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('remain', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('date', sqlalchemy.Date(), nullable=False)
))


async def update_balance(balance: List, account: Dict, engine: Engine):
    async with engine.acquire() as conn:
        existed = {}
        query = sqlalchemy.select([table]).where(
            table.c.account_id == account.get('id')).order_by(table.c.date.asc())

        async for item in conn.execute(query):
            key = item.date.strftime('%m-%Y')
            existed[key] = {
                'id': item.id,
                'income': item.income,
                'expense': item.expense,
                'remain': item.remain,
                'date': item.date
            }

        for item in balance:
            existed_id = None
            key = item['date'].strftime('%m-%Y')
            if key in existed:
                existed_id = existed[key]['id']

            if existed_id:
                query = table.update().where(table.c.id == existed_id).values(
                    account_id=account.get('id'), **item)
            else:
                query = sqlalchemy.insert(table, values={
                    'account_id': account.get('id'), **item
                })

            await conn.execute(query)
