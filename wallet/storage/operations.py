import re
from typing import Iterable, List

from asyncpg.connection import Connection  # type: ignore
from asyncpg.exceptions import UniqueViolationError  # type: ignore

from wallet.domain import EntityAlreadyExist
from wallet.domain.entities import Operation, OperationType, Tag
from wallet.domain.storage import OperationQuery, OperationRepo


class OperationsDBRepo(OperationRepo):
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

    async def add(self, instance: Operation) -> int:
        query = """
          INSERT INTO operations (
              amount, account_id, type, description, created_on
          ) VALUES ($1, $2, $3, $4, $5) RETURNING id;
        """
        key = await self._conn.fetchval(query, instance.amount, instance.account.key,
                                        instance.type.value, instance.description,
                                        instance.created_on)

        query = """
          INSERT INTO operation_tags (operation_id, tag_id) VALUES ($1, $2);
        """
        await self._conn.executemany(query, [(key, tag.key) for tag in instance.tags])

        return key

    async def find(self, query: OperationQuery) -> List[Operation]:
        parts = ["enabled = TRUE", "AND account_id = $1"]
        args = [query.account.key]

        if query.key:
            parts.append("AND id = $2")
            args.append(query.key)

        rows = await self._conn.fetch(f"""
          SELECT id, amount, type, description, created_on FROM operations
          WHERE ({' '.join(parts)}) ORDER BY created_on DESC;
        """, *args)

        return [
            Operation(row["id"], row["amount"], query.account, row["description"],
                      OperationType(row["type"]), created_on=row["created_on"])
            for row in rows
        ]

    async def update(self, instance: Operation, fields=Iterable[str]) -> bool:
        pass

    async def remove(self, instance: Operation) -> bool:
        query = """
          UPDATE operations SET enabled = FALSE
          WHERE id = $1 AND account_id = $2 AND enabled = TRUE
        """

        result = await self._conn.execute(query, instance.key, instance.account.key)

        return self._check_update(result)

    async def add_tag(self, instance: Operation, tag: Tag) -> bool:
        try:
            result = await self._conn.execute("""
              INSERT INTO operation_tags (operation_id, tag_id) VALUES ($1, $2);
            """, instance.key, tag.key)
        except UniqueViolationError:
            raise EntityAlreadyExist()

        count = 0
        match = re.search(r"\s(?P<count>\d+)$", result)
        if match:
            try:
                count = int(match.group("count"))
            except ValueError:
                pass

        return count > 0

    async def remove_tag(self, instance: Operation, tag: Tag) -> bool:
        result = await self._conn.execute("""
          DELETE FROM operation_tags WHERE operation_id = $1 AND tag_id = $2;
        """, instance.key, tag.key)

        count = 0
        match = re.search(r"DELETE\s(?P<count>\d+)", result)
        if match:
            try:
                count = int(match.group("count"))
            except ValueError:
                pass

        return count > 0
