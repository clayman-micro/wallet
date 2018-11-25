import re
from typing import Iterable, List

from asyncpg.connection import Connection  # type: ignore

from wallet.domain import Repo
from wallet.domain.entities import Operation, OperationType
from wallet.domain.storage import OperationQuery


class OperationsDBRepo(Repo[Operation, OperationQuery]):
    __slots__ = ('_conn', )

    def __init__(self, connection: Connection) -> None:
        self._conn = connection

    def _check_update(self, result: str) -> bool:
        count = 0
        match = re.search(r'UPDATE\s(?P<count>\d+)', result)
        if match:
            try:
                count = int(match.group('count'))
            except ValueError:
                pass

        return count > 0

    async def add(self, instance: Operation) -> int:
        query = """
          INSERT INTO operations (
              amount, account_id, type, description, created_on
          ) VALUES ($1, $2, $3, $4, $5) RETURNING id;
        """

        key = await self._conn.fetchval(
            query, instance.amount, instance.account.key, instance.type.value,
            instance.description, instance.created_on
        )

        await self._conn.executemany("""
          INSERT INTO operation_tags (operation_id, tag_id) VALUES ($1, $2);
        """, [(key, tag.key) for tag in instance.tags])

        return key

    async def find(self, query: OperationQuery) -> List[Operation]:
        parts = ['enabled = TRUE', 'AND account_id = $1']
        args = [query.account.key]

        if query.key:
            parts.append('AND id = $2')
            args.append(query.key)

        rows = await self._conn.fetch(f"""
          SELECT id, amount, type, description, created_on FROM operations
          WHERE ({' '.join(parts)}) ORDER BY created_on DESC;
        """, *args)

        return [
            Operation(
                row['id'], row['amount'], query.account, row['description'],
                OperationType(row['type']), created_on=row['created_on']
            ) for row in rows
        ]

    async def update(self, instance: Operation, fields=Iterable[str]) -> bool:
        pass

    async def remove(self, instance: Operation) -> bool:
        result = await self._conn.execute("""
          UPDATE operations SET enabled = FALSE
          WHERE id = $1 AND account_id = $2 AND enabled = TRUE
        """, instance.key, instance.account.key)

        return self._check_update(result)
