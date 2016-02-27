from typing import Dict

import sqlalchemy
from aiopg.sa import Engine

from .base import create_table, get_instance

table = create_table('categories', (
    sqlalchemy.Column('name', sqlalchemy.String(255), unique=True,
                      nullable=False),
    sqlalchemy.Column('owner_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id'))
))


async def get_category(instance_id, owner: Dict, engine: Engine) -> Dict:
    category = await get_instance(
        sqlalchemy.select([table])
            .where(sqlalchemy.and_(
                table.c.id == instance_id,
                table.c.owner_id == owner.get('id')
            )),
        engine=engine
    )
    return category
