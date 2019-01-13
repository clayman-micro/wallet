from typing import Iterable, List

import pendulum  # type: ignore
from asyncpg.connection import Connection  # type: ignore

from wallet.domain import Account, Operation, Tag


async def prepare_accounts(conn: Connection, accounts: List[Account]) -> List[Account]:
    now = pendulum.today()

    for account in accounts:
        query = """
          INSERT INTO accounts (name, user_id, enabled, created_on)
          VALUES ($1, $2, $3, $4) RETURNING id;
        """
        account.key = await conn.fetchval(query, account.name, account.user.key, True, now)

        query = """
          INSERT INTO balance (rest, expenses, incomes, month, account_id)
          VALUES ($1, $2, $3, $4, $5);
        """
        await conn.executemany(
            query,
            [
                (item.rest, item.expenses, item.incomes, item.month, account.key)
                for item in account.balance
            ],
        )

    return accounts


async def prepare_operations(
    conn: Connection, operations: Iterable[Operation]
) -> Iterable[Operation]:
    query = """
        INSERT INTO operations (
            amount, account_id, type, description, created_on
        ) VALUES ($1, $2, $3, $4, $5) RETURNING id;
    """

    for operation in operations:
        operation.key = await conn.fetchval(
            query,
            operation.amount,
            operation.account.key,
            operation.type.value,
            operation.description,
            operation.created_on,
        )

        if operation.tags:
            await conn.executemany("""
              INSERT INTO operation_tags (operation_id, tag_id) VALUES ($1, $2);
            """, [(operation.key, tag.key) for tag in operation.tags])

    return operations


async def prepare_tags(conn: Connection, tags: Iterable[Tag]) -> Iterable[Tag]:
    now = pendulum.today()

    query = """
      INSERT INTO tags (name, user_id, enabled, created_on)
      VALUES ($1, $2, $3, $4) RETURNING id;
    """

    for tag in tags:
        tag.key = await conn.fetchval(query, tag.name, tag.user.key, True, now)

    return tags
