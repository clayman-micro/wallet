from datetime import datetime
from typing import AsyncGenerator

import sqlalchemy  # type: ignore
from aiohttp_storage.storage import metadata  # type: ignore
from databases import Database
from passport.domain import User
from sqlalchemy.orm import Query  # type: ignore

from wallet.core.entities import Account, AccountFilters
from wallet.core.storage.accounts import AccountRepo


accounts = sqlalchemy.Table(
    "accounts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("user", sqlalchemy.Integer),
    sqlalchemy.Column("enabled", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column("created_on", sqlalchemy.DateTime, default=datetime.utcnow),
)


class AccountDBRepo(AccountRepo):
    def __init__(self, database: Database) -> None:
        self._database = database

    def _get_query(self, *, user: User) -> Query:
        query = sqlalchemy.select([accounts.c.id, accounts.c.name]).where(accounts.c.user == user.key)

        return query

    def _process_row(self, row, *, user: User) -> Account:
        account = Account(name=row["name"], user=user)
        account.key = row["id"]

        return account

    async def fetch(self, filters: AccountFilters) -> AsyncGenerator[Account, None]:
        query = self._get_query(user=filters.user)

        if filters.keys:
            query = query.where(accounts.c.id.in_(filters.keys))

        async for row in self._database.iterate(query=query):
            yield self._process_row(row, user=filters.user)

    async def fetch_by_key(self, user: User, key: int) -> Account:
        row = await self._database.fetch_one(query=self._get_query(user=user).where(accounts.c.id == key))

        return self._process_row(row, user=user)

    async def exists(self, filters: AccountFilters) -> bool:
        query = (
            sqlalchemy.select([sqlalchemy.func.count(accounts.c.id)])
            .select_from(accounts)
            .where(sqlalchemy.and_(accounts.c.user == filters.user.key, accounts.c.name == filters.name))
        )

        exists = await self._database.fetch_val(query=query)

        return exists > 0

    async def save(self, entity: Account) -> int:
        key = await self._database.execute(
            accounts.insert().returning(accounts.c.id),
            values={"name": entity.name, "user": entity.user.key, "enabled": True, "created_on": datetime.now()},
        )

        return key

    async def remove(self, entity: Account) -> bool:
        pass

    async def fetch_by_name(self, user: User, name: str) -> Account:
        row = await self._database.fetch_one(query=self._get_query(user=user).where(accounts.c.name == name))

        return self._process_row(row, user=user)
