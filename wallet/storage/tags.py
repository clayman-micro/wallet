import re
from datetime import datetime
from typing import Iterable, List

from asyncpg.connection import Connection  # type: ignore
from asyncpg.exceptions import UniqueViolationError  # type: ignore

from wallet.domain import EntityAlreadyExist, Repo
from wallet.domain.entities import Tag
from wallet.domain.storage import TagQuery


class TagsDBRepo(Repo[Tag, TagQuery]):
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

    async def add(self, instance: Tag) -> int:
        now = datetime.now()

        try:
            key = await self._conn.fetchval(
                """
              INSERT INTO tags (name, user_id, enabled, created_on)
              VALUES ($1, $2, $3, $4) RETURNING id;
            """,
                instance.name,
                instance.user.key,
                True,
                now,
            )
        except UniqueViolationError:
            raise EntityAlreadyExist()

        return key

    async def find(self, query: TagQuery) -> List[Tag]:
        parts = ["enabled = TRUE"]

        args = [query.user.key]
        if query.key:
            args.append(query.key)
            parts.append(f"AND id = $2")
        else:
            if query.name:
                parts.append(f"AND name LIKE '{query.name}%'")

        parts.append("AND user_id = $1")

        rows = await self._conn.fetch(
            f"""
          SELECT id, name FROM tags WHERE ({' '.join(parts)})
          ORDER BY tags.created_on ASC;
        """,
            *args,
        )

        return [Tag(row["id"], row["name"], query.user) for row in rows]

    async def update(self, instance: Tag, fields: Iterable[str]) -> bool:
        updated = False

        if "name" in fields:
            try:
                result = await self._conn.execute(
                    """
                  UPDATE tags SET name = $3
                  WHERE id = $1 AND user_id = $2 AND enabled = TRUE
                """,
                    instance.key,
                    instance.user.key,
                    instance.name,
                )
            except UniqueViolationError:
                result = "UPDATE 0"

            updated = self._check_update(result)

        return updated

    async def remove(self, instance: Tag) -> bool:
        result = await self._conn.execute(
            """
          UPDATE tags SET enabled = FALSE
          WHERE id = $1 AND user_id = $2 AND enabled = TRUE
        """,
            instance.key,
            instance.user.key,
        )

        return self._check_update(result)
