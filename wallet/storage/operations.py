import re
from datetime import date
from typing import Dict, Iterable, List, Optional

from asyncpg.connection import Connection  # type: ignore
from asyncpg.exceptions import UniqueViolationError  # type: ignore

from wallet.domain import Account, Operation, OperationType, Tag
from wallet.domain.storage import EntityAlreadyExist, EntityNotFound, OperationRepo


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

    async def add(self, operation: Operation) -> int:
        query = """
          INSERT INTO operations (
              amount, account_id, type, description, created_on
          ) VALUES ($1, $2, $3, $4, $5) RETURNING id;
        """
        key = await self._conn.fetchval(query, operation.amount, operation.account.key,
                                        operation.type.value, operation.description,
                                        operation.created_on)

        query = """
          INSERT INTO operation_tags (operation_id, tag_id) VALUES ($1, $2);
        """
        await self._conn.executemany(query, [(key, tag.key) for tag in operation.tags])

        return key

    async def _fetch(self, filters: str, account: Account, *args) -> Dict[int, Operation]:
        result = {}

        rows = await self._conn.fetch(f"""
          SELECT id, amount, type, description, created_on FROM operations
          WHERE ({filters}) ORDER BY created_on DESC;
        """, account.key, *args)

        for row in rows:
            result[row["id"]] = Operation(
                key=row["id"],
                amount=row["amount"],
                account=account,
                description=row["description"],
                type=OperationType(row["type"]),
                created_on=row["created_on"]
            )

        return result

    async def find(self, account: Account, month: Optional[date] = None) -> List[Operation]:
        filters = "enabled = TRUE AND account_id = $1"
        result = await self._fetch(filters, account)

        return list(result.values())

    async def find_by_key(self, account: Account, key: int) -> Operation:
        filters = "enabled = TRUE AND account_id = $1 AND id = $2"
        result = await self._fetch(filters, account, key)

        if key not in result:
            raise EntityNotFound()

        return result[key]

    async def update(self, operation: Operation, fields: Iterable[str]) -> bool:
        pass

    async def remove(self, operation: Operation) -> bool:
        query = """
          UPDATE operations SET enabled = FALSE
          WHERE id = $1 AND account_id = $2 AND enabled = TRUE
        """

        result = await self._conn.execute(query, operation.key, operation.account.key)

        return self._check_update(result)

    async def add_tag(self, operation: Operation, tag: Tag) -> bool:
        try:
            result = await self._conn.execute("""
              INSERT INTO operation_tags (operation_id, tag_id) VALUES ($1, $2);
            """, operation.key, tag.key)
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

    async def remove_tag(self, operation: Operation, tag: Tag) -> bool:
        result = await self._conn.execute("""
          DELETE FROM operation_tags WHERE operation_id = $1 AND tag_id = $2;
        """, operation.key, tag.key)

        count = 0
        match = re.search(r"DELETE\s(?P<count>\d+)", result)
        if match:
            try:
                count = int(match.group("count"))
            except ValueError:
                pass

        return count > 0
