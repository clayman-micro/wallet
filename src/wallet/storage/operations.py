from datetime import datetime

import sqlalchemy  # type: ignore
from aiohttp_storage.storage import metadata  # type: ignore
from passport.domain import User
from sqlalchemy.orm import Query

from wallet.core.entities import (
    Operation,
    OperationDependencies,
    OperationFilters,
    OperationStream,
    OperationType,
)
from wallet.core.storage.operations import OperationRepo
from wallet.storage.base import DBRepo


operations = sqlalchemy.Table(
    "operations",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("amount", sqlalchemy.Numeric(20, 2), nullable=False),
    sqlalchemy.Column("type", sqlalchemy.Enum(OperationType), nullable=False),
    sqlalchemy.Column("desc", sqlalchemy.String(500)),
    sqlalchemy.Column("user", sqlalchemy.Integer),
    sqlalchemy.Column(
        "account_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sqlalchemy.Column(
        "category_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("categories.id", ondelete="CASCADE"),
    ),
    sqlalchemy.Column("enabled", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column(
        "created_on", sqlalchemy.DateTime, default=datetime.utcnow
    ),
)


class OperationDBRepo(DBRepo, OperationRepo):
    def _get_query(self, *, user: User) -> Query:
        query = (
            sqlalchemy.select(
                [
                    operations.c.id,
                    operations.c.amount,
                    operations.c.type,
                    operations.c.desc,
                    operations.c.account_id,
                    operations.c.category_id,
                    operations.c.created_on,
                ]
            )
            .where(
                sqlalchemy.and_(
                    operations.c.user == user.key,
                    operations.c.enabled == True,  # noqa:E712
                )
            )
            .order_by(operations.c.created_on.desc())
        )

        return query

    def _process_row(self, row, *, user: User) -> Operation:
        operation = Operation(
            amount=row["amount"],
            description=row["desc"],
            operation_type=row["type"],
            user=user,
        )
        operation.key = row["id"]
        operation.created_on = row["created_on"]

        return operation

    async def fetch(self, filters: OperationFilters) -> OperationStream:
        query = self._get_query(user=filters.user)

        async for row in self._database.iterate(query=query):
            dependencies = OperationDependencies(account=1, category=1)

            yield self._process_row(row, user=filters.user), dependencies

    async def fetch_by_key(self, user: User, key: int) -> Operation:
        row = await self._database.fetch_one(
            query=self._get_query(user=user).where(operations.c.id == key)
        )

        return self._process_row(row, user=user)

    async def save(self, entity: Operation) -> int:
        key = await self._database.execute(
            operations.insert().returning(operations.c.id),
            values={
                "amount": entity.amount,
                "type": entity.operation_type.value,
                "desc": entity.description,
                "user": entity.user.key,
                "account_id": entity.account.key,
                "category_id": entity.category.key,
                "enabled": True,
                "created_on": entity.created_on,
            },
        )

        return key

    async def remove(self, entity: Operation) -> bool:
        pass
