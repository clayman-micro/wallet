from datetime import datetime
from typing import AsyncGenerator

import sqlalchemy  # type: ignore
from aiohttp_storage.storage import metadata  # type: ignore
from asyncpg.exceptions import UniqueViolationError
from passport.domain import User
from sqlalchemy.orm import Query

from wallet.core.entities import Account, AccountFilters
from wallet.core.exceptions import AccountAlreadyExist, AccountNotFound
from wallet.core.storage.accounts import AccountRepo
from wallet.storage.abc import DBRepo

accounts = sqlalchemy.Table(
    "accounts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("user", sqlalchemy.Integer),
    sqlalchemy.Column("enabled", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column("created_on", sqlalchemy.DateTime, default=datetime.utcnow),
)


class AccountDBRepo(AccountRepo, DBRepo[Account, AccountFilters]):
    """Repository to get access to Accounts storage."""

    def _get_query(self, filters: AccountFilters) -> Query:
        query = sqlalchemy.select([accounts.c.id, accounts.c.name]).where(
            sqlalchemy.and_(accounts.c.user == filters.user.key, accounts.c.enabled == True)  # noqa: E712
        )

        if filters.keys:
            query = query.where(accounts.c.id.in_(filters.keys))

        return query

    def _process_row(self, row, **kwargs) -> Account:
        account = Account(name=row["name"], user=kwargs["user"])
        account.key = row["id"]

        return account

    async def fetch(self, filters: AccountFilters) -> AsyncGenerator[Account, None]:
        """Fetch accounts from storage.

        Args:
            filters: Params to filter accounts.

        Returns:
            Account instances from storage.
        """
        query = self._get_query(filters)

        async for row in self._database.iterate(query=query):
            yield self._process_row(row, user=filters.user)

    async def fetch_by_key(self, user: User, key: int) -> Account:
        """Fetch account by key.

        Args:
            user: Account owner.
            key: Account identifier.

        Returns:
            Account instance.
        """
        query = self._get_query(filters=AccountFilters(user=user)).where(accounts.c.id == key)
        row = await self._database.fetch_one(query=query)

        if not row:
            raise AccountNotFound(user=user, name="")

        return self._process_row(row, user=user)

    async def fetch_by_name(self, user: User, name: str) -> Account:
        """Fetch account by it's name.

        Args:
            user: Account owner instance.
            name: Account name.

        Returns:
            Account instance.
        """
        query = self._get_query(filters=AccountFilters(user=user)).where(accounts.c.name == name)
        row = await self._database.fetch_one(query=query)

        if not row:
            raise AccountNotFound(user=user, name=name)

        return self._process_row(row, user=user)

    async def exists(self, filters: AccountFilters) -> bool:
        """Check if accounts exist in storage.

        Args:
            filters: Params to filter accounts.

        Returns:
            Accounts exist in storage.
        """
        query = (
            sqlalchemy.select([sqlalchemy.func.count(accounts.c.id)])
            .select_from(accounts)
            .where(sqlalchemy.and_(accounts.c.user == filters.user.key, accounts.c.name == filters.name))
        )

        exists = await self._database.fetch_val(query=query)

        return exists > 0

    async def save(self, entity: Account) -> int:
        """Save account changes to storage.

        Args:
            entity: Account instance.
        """
        try:
            key = await self._database.execute(
                accounts.insert().returning(accounts.c.id),
                values={"name": entity.name, "user": entity.user.key, "enabled": True, "created_on": datetime.now()},
            )
        except UniqueViolationError:
            raise AccountAlreadyExist(user=entity.user, account=entity)

        return key

    async def remove(self, entity: Account) -> bool:
        """Remove account from storage.

        Args:
            entity: Account instance.
        """
        query = accounts.update(
            sqlalchemy.and_(accounts.c.user == entity.user.key, accounts.c.id == entity.key), values={"enabled": False},
        ).returning(accounts.c.id)

        result = await self._database.fetch_val(query=query)

        if result is None:
            raise AccountNotFound(entity.user, name=entity.name)

        return result == entity.key
