import re
from typing import Iterable, List, Optional

from asyncpg.connection import Connection

from wallet.entities import EntityAlreadyExist, EntityNotFound, Owner, Tag


Tags = List[Tag]


class TagsRepository(object):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

        self._update_pattern = re.compile(r'UPDATE (?P<count>\d+)')

    def _did_update(self, result):
        match = self._update_pattern.search(result)
        if match:
            try:
                count = int(match.group('count'))
            except ValueError:
                count = 0

        return count > 0

    async def fetch(self, owner: Owner, name: Optional[str] = None) -> Tags:
        tags = []

        async with self._conn.transaction():
            query = ['SELECT id, name FROM tags WHERE (enabled = True']

            if name:
                query.append(f"AND name LIKE '{name}%'")

            query.append('AND owner_id = $1) ORDER BY created_on ASC;')

            async for row in self._conn.cursor(' '.join(query), owner.pk):
                tag = Tag(row['name'], owner, pk=row['id'])
                tags.append(tag)

        return tags

    async def fetch_tag(self, owner: Owner, pk: int) -> Tag:
        query = '''
            SELECT id, name FROM tags
            WHERE enabled = TRUE AND owner_id = $1 AND id = $2;
        '''

        row = await self._conn.fetchrow(query, owner.pk, pk)

        if not row:
            raise EntityNotFound()

        return Tag(row['name'], owner, pk=row['id'])

    async def save_tag(self, tag: Tag) -> int:
        query = 'SELECT COUNT(id) FROM tags WHERE name = $1 AND owner_id = $2;'

        async with self._conn.transaction():
            count = await self._conn.fetchval(query, tag.name, tag.owner.pk)

            if count:
                raise EntityAlreadyExist()

            query = '''
                INSERT INTO tags (name, enabled, owner_id, created_on)
                VALUES ($1, $2, $3, $4) RETURNING id;
            '''

            pk = await self._conn.fetchval(query, tag.name, tag.enabled,
                                           tag.owner.pk, tag.created_on)

        return pk

    async def update_tag(self, tag: Tag, fields: Iterable[str]) -> bool:
        allowed = ('name', )

        index = 2
        parts = []
        args = []

        for field in fields:
            if field in allowed:
                parts.append(f'{field} = ${index}')
                args.append(getattr(tag, field))
                index += 1

        async with self._conn.transaction():
            if 'name' in fields:
                count = await self._conn.fetchval('''
                    SELECT COUNT(id) FROM tags
                    WHERE name = $1 AND owner_id = $2 AND id != $3
                ''', tag.name, tag.owner.pk, tag.pk)

                if count:
                    raise EntityAlreadyExist()

            if parts:
                query = f'UPDATE tags SET {", ".join(parts)} WHERE id = $1;'
                result = await self._conn.execute(query, tag.pk, *args)
                return self._did_update(result)
            else:
                return False

    async def remove_tag(self, tag: Tag) -> bool:
        query = '''
            UPDATE tags SET enabled = FALSE
            WHERE id = $1 AND owner_id = $2 AND enabled = TRUE;
        '''
        async with self._conn.transaction():
            result = await self._conn.execute(query, tag.pk, tag.owner.pk)

        return self._did_update(result)
