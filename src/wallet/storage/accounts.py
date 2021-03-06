import re
from datetime import datetime
from itertools import groupby
from typing import Dict, Iterable, List

import pendulum  # type: ignore
from asyncpg.connection import Connection  # type: ignore
from asyncpg.exceptions import UniqueViolationError  # type: ignore

from wallet.domain import Account, Balance, User
from wallet.domain.storage import (
    AccountsRepo,
    EntityAlreadyExist,
    EntityNotFound,
)


class AccountsDBRepo(AccountsRepo):
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

    async def _fetch(
        self, filters: str, user: User, *args
    ) -> Dict[int, Account]:
        rows = await self._conn.fetch(
            f"""
          SELECT
            accounts.id as id,
            accounts.name as name,
            balance.rest as rest,
            balance.expenses as expenses,
            balance.incomes as incomes,
            balance.month as month
          FROM accounts
            INNER JOIN balance ON (accounts.id = balance.account_id)
          WHERE ({filters})
          ORDER BY accounts.created_on ASC, balance.month DESC;
        """,
            user.key,
            *args,
        )

        result = {}

        for key, group in groupby(
            rows, key=lambda item: (item["id"], item["name"])
        ):
            balance = [
                Balance(
                    rest=item["rest"],
                    expenses=item["expenses"],
                    incomes=item["incomes"],
                    month=pendulum.date(
                        item["month"].year,
                        item["month"].month,
                        item["month"].day,
                    ),
                )
                for item in group
            ]

            account = Account(
                key=key[0], name=key[1], user=user, balance=balance
            )
            result[key[0]] = account

        return result

    async def find(self, user: User) -> List[Account]:
        filters = "accounts.enabled = TRUE AND accounts.user_id = $1"
        result = await self._fetch(filters, user)

        return list(result.values())

    async def find_by_key(self, user: User, key: int) -> Account:
        filters = "accounts.enabled = TRUE AND accounts.user_id = $1 AND accounts.id = $2"
        result = await self._fetch(filters, user, key)

        if key not in result:
            raise EntityNotFound

        return result[key]

    async def find_by_name(self, user: User, name: str) -> List[Account]:
        filters = f"accounts.enabled = TRUE AND accounts.user_id = $1 AND name LIKE '{name}%'"
        result = await self._fetch(filters, user)

        return list(result.values())

    async def add(self, operation: Account) -> int:
        now = datetime.now()

        try:
            key = await self._conn.fetchval(
                """
              INSERT INTO accounts (name, user_id, enabled, created_on)
              VALUES ($1, $2, $3, $4) RETURNING id;
            """,
                operation.name,
                operation.user.key,
                True,
                now,
            )
        except UniqueViolationError:
            raise EntityAlreadyExist()

        query = """
          INSERT INTO balance (rest, expenses, incomes, month, account_id)
          VALUES ($1, $2, $3, $4, $5);
        """

        await self._conn.executemany(
            query,
            [
                (entry.rest, entry.expenses, entry.incomes, entry.month, key)
                for entry in operation.balance
            ],
        )

        return key

    async def _update_name(self, instance: Account) -> str:
        try:
            result = await self._conn.execute(
                """
              UPDATE accounts SET name = $3
              WHERE id = $1 AND user_id = $2 AND enabled = TRUE
            """,
                instance.key,
                instance.user.key,
                instance.name,
            )
        except UniqueViolationError:
            result = "UPDATE 0"

        return result

    async def _update_balance(self, instance: Account) -> List[str]:
        results = []

        query = "SELECT month FROM balance WHERE account_id = $1"
        existed = await self._conn.fetch(query, instance.key)

        existed_months = [row["month"] for row in existed]

        for item in instance.balance:
            if item.month in existed_months:
                query = """
                  UPDATE balance SET rest = $3, expenses = $4, incomes = $5
                  WHERE account_id = $1 AND month = $2;
                """
            else:
                query = """
                  INSERT INTO balance (account_id, month, rest, expenses, incomes)
                  VALUES ($1, $2, $3, $4, $5);
                """

            result = await self._conn.execute(
                query,
                instance.key,
                item.month,
                item.rest,
                item.expenses,
                item.incomes,
            )
            results.append(result)

        return results

    async def update(self, operation: Account, fields: Iterable[str]) -> bool:
        updated = False

        if "name" in fields:
            result = await self._update_name(operation)

            updated = self._check_update(result)

        if "balance" in fields:
            results = await self._update_balance(operation)

            count = 0
            for result in results:
                match = re.search(r"\s(?P<count>\d+)$", result)
                if match:
                    try:
                        count += int(match.group("count"))
                    except ValueError:
                        continue

            updated = count == len(operation.balance)

        return updated

    async def remove(self, operation: Account) -> bool:
        result = await self._conn.execute(
            """
          UPDATE accounts SET enabled = FALSE
          WHERE id = $1 AND user_id = $2 AND enabled = TRUE
        """,
            operation.key,
            operation.user.key,
        )

        return self._check_update(result)
