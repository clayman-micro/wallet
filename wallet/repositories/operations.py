import re
from datetime import datetime
from typing import List

from asyncpg.connection import Connection

from wallet.entities import Account, EntityNotFound, Operation, OperationType


Operations = List[Operation]


class OperationsRepo(object):
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

    async def fetch_operations(self, account: Account) -> Operations:
        operations = []

        query = '''
            SELECT
                id, type, amount, description, created_on
            FROM operations
            WHERE (
                enabled = True AND owner_id = $1 AND account_id = $2
            ) ORDER BY created_on DESC;
        '''

        async with self._conn.transaction():
            args = (account.owner.pk, account.pk)
            async for row in self._conn.cursor(query, *args):
                operation = Operation(
                    row['amount'], account, pk=row['id'],
                    type=getattr(OperationType, row['type'].upper()),
                    description=row['description'],
                    created_on=row['created_on']
                )
                operations.append(operation)
        return operations

    async def fetch(self, account: Account, year: int, month: int) -> Operations:
        operations = []

        query = '''
            SELECT
                id, type, amount, description, created_on
            FROM operations
            WHERE (
                enabled = True AND owner_id = $1 AND account_id = $2
                AND created_on >= $3 AND created_on < $3 + interval '1 month'
            ) ORDER BY created_on DESC;
        '''

        async with self._conn.transaction():
            args = (account.owner.pk, account.pk, datetime(year, month, 1))
            async for row in self._conn.cursor(query, *args):
                operation = Operation(
                    row['amount'], account, pk=row['id'],
                    type=getattr(OperationType, row['type'].upper()),
                    description=row['description'],
                    created_on=row['created_on']
                )
                operations.append(operation)
        return operations

    async def fetch_operation(self, account: Account, pk: int) -> Operation:
        query = '''
            SELECT
                id, type, amount, description, created_on
            FROM operations
            WHERE (
                enabled = True AND owner_id = $1 AND account_id = $2 AND id = $3
            )
        '''
        row = await self._conn.fetchrow(query, account.owner.pk, account.pk, pk)
        if not row:
            raise EntityNotFound()

        operation = Operation(
            row['amount'], account, pk=row['id'], created_on=row['created_on'],
            type=getattr(OperationType, row['type'].upper()),
            description=row['description']
        )

        return operation

    async def save(self, operation: Operation) -> int:
        query = '''
            INSERT INTO operations (
                type, amount, account_id, enabled, owner_id, created_on
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        '''

        pk = await self._conn.fetchval(
            query, operation.type.value.lower(), operation.amount,
            operation.account.pk, operation.enabled,
            operation.account.owner.pk, operation.created_on
        )

        return pk

    async def update(self, operation: Operation, fields: List[str]) -> bool:
        allowed = ('amount', 'type', 'description', 'created_on')

        index = 2
        query_parts = []
        args = []
        for field in fields:
            if field in allowed:
                query_parts.append(f'{field} = ${index}')
                value = getattr(operation, field)

                if field == 'type':
                    value = value.value.lower()

                args.append(value)
                index += 1

        if query_parts:
            query = f'''
                UPDATE operations SET {", ".join(query_parts)}
                WHERE id = $1 AND enabled = TRUE
            '''

            result = await self._conn.execute(query, operation.pk, *args)

            return self._did_update(result)
        else:
            return False

    async def remove(self, operation: Operation) -> bool:
        query = '''
            UPDATE operations SET enabled = FALSE
            WHERE (
                id = $1 AND account_id = $2
                AND owner_id = $3 AND enabled = TRUE
            )
        '''

        result = await self._conn.execute(
            query, operation.pk, operation.account.pk,
            operation.account.owner.pk
        )

        return self._did_update(result)
