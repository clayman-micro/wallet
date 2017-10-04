import re
from datetime import datetime
from typing import Dict, List

from asyncpg.connection import Connection

from wallet.storage import AlreadyExist, Resource, ResourceNotFound
from wallet.storage.owner import Owner


update_pattern = re.compile(r'UPDATE (?P<count>\d+)')


class Tag(Resource):
    __slots__ = (
        'id', 'name', 'enabled', 'owner_id', 'created_on'
    )

    def __init__(self, name: str, owner: Owner, **optional) -> None:
        self.name = name

        super(Tag, self).__init__(owner, **optional)

    def serialize(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name
        }


async def fetch_tags(owner: Owner, conn: Connection, **search) -> List[Tag]:
    result = []

    async with conn.transaction():
        if 'name' in search and search['name']:
            query = f'''
                SELECT id, name FROM tags
                WHERE (
                    enabled = TRUE AND owner_id = $1
                    AND name LIKE '{search['name']}%'
                )
                ORDER BY created_on ASC
            '''
        else:
            query = '''
                SELECT id, name FROM tags
                WHERE enabled = TRUE AND owner_id = $1
                ORDER BY created_on ASC
            '''
        async for row in conn.cursor(query, owner.id):
            tag = Tag(row['name'], owner, id=row['id'])
            result.append(tag)

    return result


async def fetch_tag(owner: Owner, tag_id: int, conn: Connection) -> Tag:
    query = '''
        SELECT id, name FROM tags
        WHERE enabled = TRUE AND owner_id = $1 AND id = $2
    '''
    row = await conn.fetchrow(query, owner.id, tag_id)

    if not row:
        raise ResourceNotFound()

    tag = Tag(row['name'], owner, id=row['id'])
    return tag


async def add_tag(owner: Owner, name: str, created: datetime,
                  conn: Connection) -> Tag:

    tag = Tag(name, owner, created_on=created)

    async with conn.transaction():
        query = 'SELECT COUNT(id) FROM tags WHERE name = $1 AND owner_id = $2'
        count = await conn.fetchval(query, name, owner.id)
        if count:
            raise AlreadyExist()

        query = '''
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        '''
        tag.id = await conn.fetchval(query, tag.name, tag.enabled, tag.owner_id,
                                     tag.created_on)

    return tag


async def rename_tag(tag: Tag, name: str, conn: Connection) -> bool:

    async with conn.transaction():
        query = '''
            SELECT COUNT(id) FROM tags
            WHERE (
                id != $1 AND owner_id = $2 AND enabled = TRUE AND name = $3
            )
        '''
        count = await conn.fetchval(query, tag.id, tag.owner_id, name)
        if count:
            raise AlreadyExist()

        query = '''
            UPDATE tags SET name = $1 WHERE id = $2 AND owner_id = $3
        '''
        result = await conn.execute(query, name, tag.id, tag.owner_id)

    match = update_pattern.search(result)
    if match:
        try:
            count = int(match.group('count'))
        except ValueError:
            pass

    return count > 0


async def remove_tag(tag: Tag, conn: Connection) -> bool:
    count = 0

    async with conn.transaction():
        query = '''
            UPDATE tags SET enabled = FALSE
            WHERE id = $1 AND owner_id = $2 AND enabled = TRUE
        '''
        result = await conn.execute(query, tag.id, tag.owner_id)

    match = update_pattern.search(result)
    if match:
        try:
            count = int(match.group('count'))
        except ValueError:
            pass

    return count > 0
