import re
from datetime import datetime
from typing import Dict, List

from asyncpg.connection import Connection

from wallet.storage import AlreadyExist, ResourceNotFound


async def fetch_tags(owner: Dict, conn: Connection) -> List[Dict]:
    result = []

    query = '''
        SELECT id, name FROM tags
        WHERE enabled = TRUE AND owner_id = $1
        ORDER BY created_on ASC
    '''
    async with conn.transaction():
        async for row in conn.cursor(query, owner['id']):
            result.append({'id': row['id'], 'name': row['name']})

    return result


async def fetch_tag(owner: Dict, tag_id: int, conn: Connection) -> Dict:
    query = '''
        SELECT id, name FROM tags
        WHERE enabled = TRUE AND owner_id = $1 AND id = $2
    '''
    row = await conn.fetchrow(query, owner['id'], tag_id)

    if not row:
        raise ResourceNotFound()

    return {'id': row['id'], 'name': row['name']}


async def add_tag(owner: Dict, name: str, created: datetime,
                  conn: Connection) -> Dict:
    tag = {'name': name}

    async with conn.transaction():
        query = 'SELECT COUNT(id) FROM tags WHERE name = $1 AND owner_id = $2'
        count = await conn.fetchval(query, name, owner['id'])
        if count:
            raise AlreadyExist()

        query = '''
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        '''
        tag['id'] = await conn.fetchval(query, name, True, owner['id'], created)

    return tag


async def remove_tag(owner: Dict, tag: Dict, conn: Connection) -> bool:
    count = 0

    async with conn.transaction():
        query = '''
            UPDATE tags SET enabled = FALSE WHERE id = $1 AND owner_id = $2
        '''
        result = await conn.execute(query, tag['id'], owner['id'])

    match = re.search(r'UPDATE (?P<count>\d+)', result)
    if match:
        try:
            count = int(match.group('count'))
        except ValueError:
            pass

    return count > 0
