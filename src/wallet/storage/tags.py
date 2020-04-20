import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, Iterable, List

from asyncpg.connection import Connection  # type: ignore
from asyncpg.exceptions import UniqueViolationError  # type: ignore

from wallet.domain import Tag, User
from wallet.domain.storage import EntityAlreadyExist, EntityNotFound, TagsRepo


class TagsDBRepo(TagsRepo):
    __slots__ = ("_conn",)

    def __init__(self, connection: Connection) -> None:
        self._conn = connection

    def _check_update(self, result: str) -> bool:
        count = 0
        match = re.search(r"UPDATE\s(?P<count>\d+)", result)
        if match:
            try:
                count = int(match.group("count"))
            except ValueError:
                pass

        return count > 0

    async def _fetch(self, filters: str, user: User, *args) -> Dict[int, Tag]:
        result = {}

        query = f"SELECT id, name FROM tags WHERE ({filters}) ORDER BY tags.created_on ASC"  # noqa: E501
        rows = await self._conn.fetch(query, user.key, *args)

        for row in rows:
            result[row["id"]] = Tag(key=row["id"], name=row["name"], user=user)

        return result

    async def add(self, tag: Tag) -> int:
        now = datetime.now()

        try:
            key = await self._conn.fetchval(
                """
              INSERT INTO tags (name, user_id, enabled, created_on)
              VALUES ($1, $2, $3, $4) RETURNING id;
            """,
                tag.name,
                tag.user.key,
                True,
                now,
            )
        except UniqueViolationError:
            raise EntityAlreadyExist()

        return key

    async def find(self, user: User) -> List[Tag]:
        filters = "enabled = TRUE AND user_id = $1"
        result = await self._fetch(filters, user)

        return list(result.values())

    async def find_by_key(self, user: User, key: int) -> Tag:
        filters = "enabled = TRUE AND user_id = $1 AND id = $2"
        result = await self._fetch(filters, user, key)

        if key not in result:
            raise EntityNotFound

        return result[key]

    async def find_by_name(self, user: User, name: str) -> List[Tag]:
        filters = f"enabled = TRUE AND user_id = $1 AND name LIKE '{name}%'"
        result = await self._fetch(filters, user)

        return list(result.values())

    async def find_by_operations(
        self, user: User, operations: Iterable[int]
    ) -> Dict[int, List[Tag]]:
        result: Dict[int, List[Tag]] = defaultdict(list)

        query = """
          SELECT
            tags.id,
            tags.name,
            operation_tags.operation_id
          FROM tags
            INNER JOIN operation_tags ON operation_tags.tag_id = tags.id
          WHERE (
            tags.enabled = TRUE
            AND tags.user_id = $1
            AND operation_tags.operation_id = any($2::integer[])
          )
        """
        rows = await self._conn.fetch(query, user.key, operations)

        for row in rows:
            result[row["operation_id"]].append(
                Tag(row["id"], row["name"], user)
            )

        return result

    async def update(self, tag: Tag, fields: Iterable[str]) -> bool:
        updated = False

        if "name" in fields:
            try:
                result = await self._conn.execute(
                    """
                  UPDATE tags SET name = $3
                  WHERE id = $1 AND user_id = $2 AND enabled = TRUE
                """,
                    tag.key,
                    tag.user.key,
                    tag.name,
                )
            except UniqueViolationError:
                result = "UPDATE 0"

            updated = self._check_update(result)

        return updated

    async def remove(self, tag: Tag) -> bool:
        result = await self._conn.execute(
            """
          UPDATE tags SET enabled = FALSE
          WHERE id = $1 AND user_id = $2 AND enabled = TRUE
        """,
            tag.key,
            tag.user.key,
        )

        return self._check_update(result)
