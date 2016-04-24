from typing import Dict

import sqlalchemy
from aiopg.sa import SAConnection

from .base import create_table, get_instance
from .transactions import table as transactions_table


table = create_table('transaction_details', (
    sqlalchemy.Column('name', sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column('price_per_unit', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('count', sqlalchemy.Numeric(20, 3)),
    sqlalchemy.Column('total', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('transaction_id', sqlalchemy.Integer(),
                      sqlalchemy.ForeignKey('transactions.id'), nullable=False)
))


async def get_detail(instance_id, transaction: Dict, conn: SAConnection):
    join = sqlalchemy.join(table, transactions_table,
                           table.c.transaction_id == transactions_table.c.id)
    query = sqlalchemy.select([table]).select_from(join).where(
        sqlalchemy.and_(
            transactions_table.c.id == transaction.get('id'),
            table.c.id == instance_id
        )
    )
    return await get_instance(query, conn=conn)
