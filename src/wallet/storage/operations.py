from datetime import datetime

import sqlalchemy  # type: ignore
from aiohttp_storage.storage import metadata  # type: ignore
from passport.domain import User
from sqlalchemy.orm import Query  # type: ignore

from wallet.core.entities import (
    Operation,
    OperationDependencies,
    OperationFilters,
    OperationStream,
    OperationType,
)
from wallet.core.storage.operations import OperationRepo
from wallet.storage.abc import DBRepo


operations = sqlalchemy.Table(
    "operations",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("amount", sqlalchemy.Numeric(20, 2), nullable=False),
    sqlalchemy.Column("type", sqlalchemy.Enum(OperationType), nullable=False),
    sqlalchemy.Column("desc", sqlalchemy.String(500)),
    sqlalchemy.Column("user", sqlalchemy.Integer),
    sqlalchemy.Column(
        "account_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False,
    ),
    sqlalchemy.Column("category_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("categories.id", ondelete="CASCADE"),),
    sqlalchemy.Column("enabled", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column("created_on", sqlalchemy.DateTime, default=datetime.utcnow),
)


class OperationDBRepo(OperationRepo, DBRepo[Operation, OperationFilters]):
    """Repository to get access to Operations storage."""

    def _get_query(self, filters: OperationFilters) -> Query:
        query = sqlalchemy.select(
            [
                operations.c.id,
                operations.c.amount,
                operations.c.type,
                operations.c.desc,
                operations.c.account_id,
                operations.c.category_id,
                operations.c.created_on,
            ]
        ).where(
            sqlalchemy.and_(operations.c.user == filters.user.key, operations.c.enabled == True)  # noqa:E712
        )

        if filters.limit:
            query = query.limit(filters.limit)

        if filters.offset:
            query = query.offset(filters.offset)

        if filters.period:
            query = query.where(
                sqlalchemy.and_(
                    operations.c.created_on >= filters.period.beginning,
                    operations.c.created_on <= filters.period.ending,
                )
            )

        if filters.account_key:
            query = query.where(operations.c.account_id == filters.account_key)

        if filters.category_key:
            query = query.where(operations.c.category_id == filters.category_key)

        return query.order_by(operations.c.created_on.desc())

    def _process_row(self, row, **kwargs) -> Operation:
        operation = Operation(
            amount=row["amount"], description=row["desc"], operation_type=row["type"], user=kwargs["user"]
        )
        operation.key = row["id"]
        operation.created_on = row["created_on"]

        return operation

    async def fetch(self, filters: OperationFilters) -> OperationStream:
        """Fetch operations from storage.

        Args:
            filters: Params to filter operations.

        Returns:
            Operation instances from storage.
        """
        query = self._get_query(filters=filters)

        async for row in self._database.iterate(query=query):
            dependencies = OperationDependencies(account=row["account_id"], category=row["category_id"])

            yield self._process_row(row, user=filters.user), dependencies

    async def fetch_by_key(self, user: User, key: int) -> Operation:
        """Fetch operation by key.

        Args:
            user: Operation owner.
            key: Operation identifier.

        Returns:
            Operation instance.
        """
        row = await self._database.fetch_one(
            query=self._get_query(filters=OperationFilters(user=user)).where(operations.c.id == key)
        )

        return self._process_row(row, user=user)

    async def exists(self, filters: OperationFilters) -> bool:
        """Check if operations exist in storage.

        Args:
            filters: Params to filter operations.

        Returns:
            Operations exist in storage.
        """
        raise NotImplementedError()

    async def save(self, entity: Operation) -> int:
        """Save operation changes to storage.

        Args:
            entity: Operation instance.
        """
        key = await self._database.execute(
            operations.insert().returning(operations.c.id),
            values={
                "amount": entity.amount,
                "type": entity.operation_type.value,
                "desc": entity.description,
                "user": entity.user.key,
                "account_id": entity.account.key if entity.account else None,
                "category_id": entity.category.key if entity.category else None,
                "enabled": True,
                "created_on": entity.created_on,
            },
        )

        return key

    async def remove(self, entity: Operation) -> bool:
        """Remove operation from storage.

        Args:
            entity: Operation instance.
        """
        raise NotImplementedError()
