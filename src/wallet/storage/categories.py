from datetime import datetime

import sqlalchemy  # type: ignore
from aiohttp_storage.storage import metadata  # type: ignore
from databases import Database
from passport.domain import User
from sqlalchemy.orm import Query  # type: ignore

from wallet.core.entities import Category, CategoryFilters, CategoryStream
from wallet.core.exceptions import CategoryNotFound
from wallet.core.storage.categories import CategoryRepo


categories = sqlalchemy.Table(
    "categories",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("user", sqlalchemy.Integer),
    sqlalchemy.Column("enabled", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column("created_on", sqlalchemy.DateTime, default=datetime.utcnow),
)


category_tags = sqlalchemy.Table(
    "category_tags",
    metadata,
    sqlalchemy.Column(
        "category_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
    sqlalchemy.Column(
        "tag_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
)


class CategoryDBRepo(CategoryRepo):
    def __init__(self, database: Database) -> None:
        self._database = database

    def _get_query(self, *, user: User) -> Query:
        query = sqlalchemy.select([categories.c.id, categories.c.name]).where(categories.c.user == user.key)

        return query

    def _process_row(self, row, *, user: User) -> Category:
        category = Category(name=row["name"], user=user)
        category.key = row["id"]

        return category

    async def fetch(self, filters: CategoryFilters) -> CategoryStream:
        query = self._get_query(user=filters.user)

        if filters.keys:
            query = query.where(categories.c.id.in_(filters.keys))

        async for row in self._database.iterate(query=query):
            yield self._process_row(row, user=filters.user)

    async def fetch_by_key(self, user: User, key: int) -> Category:
        row = await self._database.fetch_one(query=self._get_query(user=user).where(categories.c.id == key))

        if not row:
            raise CategoryNotFound(user=user, name="")

        return self._process_row(row, user=user)

    async def fetch_by_name(self, user: User, name: str) -> Category:
        row = await self._database.fetch_one(query=self._get_query(user=user).where(categories.c.name == name))

        if not row:
            raise CategoryNotFound(user=user, name=name)

        return self._process_row(row, user=user)

    async def exists(self, filters: CategoryFilters) -> bool:
        query = (
            sqlalchemy.select([sqlalchemy.func.count(categories.c.id)])
            .select_from(categories)
            .where(sqlalchemy.and_(categories.c.user == filters.user.key, categories.c.name == filters.name,))
        )

        exists = await self._database.fetch_val(query=query)

        return exists > 0

    async def save(self, entity: Category) -> int:
        key = await self._database.execute(
            categories.insert().returning(categories.c.id),
            values={"name": entity.name, "user": entity.user.key, "enabled": True, "created_on": datetime.now()},
        )

        return key

    async def remove(self, entity: Category) -> bool:
        pass
