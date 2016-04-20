from typing import Dict

import sqlalchemy
from aiopg.sa import SAConnection

from .base import create_table, get_instance


table = create_table('categories', (
    sqlalchemy.Column('name', sqlalchemy.String(255), unique=True,
                      nullable=False),
    sqlalchemy.Column('owner_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id'))
))


async def get_category(instance_id, owner: Dict, conn: SAConnection) -> Dict:
    query = sqlalchemy.select([table]).where(sqlalchemy.and_(
        table.c.id == instance_id,
        table.c.owner_id == owner.get('id')
    ))
    return await get_instance(query, conn=conn)
