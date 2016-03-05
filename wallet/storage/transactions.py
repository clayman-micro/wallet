from typing import Dict

import sqlalchemy
from aiopg.sa import Engine

from .base import create_table, get_instance
from .accounts import table as accounts_table


INCOME_TRANSACTION = 'income'
EXPENSE_TRANSACTION = 'expense'
TRANSFER_TRANSACTION = 'transfer'
TRANSACTION_TYPES = (INCOME_TRANSACTION, EXPENSE_TRANSACTION,
                     TRANSFER_TRANSACTION)

table = create_table('transactions', (
    sqlalchemy.Column('type', sqlalchemy.String(20), nullable=False),
    sqlalchemy.Column('description', sqlalchemy.String(255)),
    sqlalchemy.Column('amount', sqlalchemy.Numeric(20, 2), nullable=False),
    sqlalchemy.Column('account_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('accounts.id'), nullable=False),
    sqlalchemy.Column('category_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('categories.id'), nullable=False),
    sqlalchemy.Column('created_on', sqlalchemy.DateTime(), nullable=False)
))


async def get_transaction(instance_id, owner: Dict, engine: Engine) -> Dict:
    join = sqlalchemy.join(table, accounts_table,
                           accounts_table.c.id == table.c.account_id)
    transaction = await get_instance(
        sqlalchemy.select([table]).select_from(join).where(sqlalchemy.and_(
            table.c.id == instance_id,
            accounts_table.c.owner_id == owner.get('id')
        )),
        engine
    )

    return transaction
