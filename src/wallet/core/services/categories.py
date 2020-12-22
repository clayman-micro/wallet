from typing import AsyncGenerator

from passport.domain import User

from wallet.core.entities import (
    Category,
    CategoryFilters,
    CategoryPayload,
    OperationFilters,
)
from wallet.core.exceptions import EntityAlreadyExist
from wallet.core.services import Service


class CategoryService(Service[Category, CategoryFilters, CategoryPayload]):
    async def add(
        self, payload: CategoryPayload, dry_run: bool = False
    ) -> Category:
        category = Category(name=payload.name, user=payload.user)

        exists = await self._storage.categories.fetch_by_name(
            user=category.user, name=category.name
        )
        if exists:
            raise EntityAlreadyExist()

        if not dry_run:
            category.key = await self._storage.categories.save(category)

        self._logger.info(
            "Add new category",
            user=category.user.key,
            name=category.name,
            dry_run=dry_run,
        )

        return category

    async def remove(self, entity: Category, dry_run: bool = False) -> None:
        filters = OperationFilters(user=entity.user, category=entity)
        has_operations = await self._storage.operations.exists(filters)
        if has_operations:
            raise Exception

        if not dry_run:
            await self._storage.categories.remove(entity=entity)

        self._logger.info(
            "Remove category",
            user=entity.user.key,
            name=entity.name,
            dry_run=dry_run,
        )

    async def find(
        self, filters: CategoryFilters
    ) -> AsyncGenerator[Category, None]:
        return await self._storage.categories.fetch(filters=filters)

    async def find_by_key(self, user: User, key: int) -> Category:
        return await self._storage.categories.fetch_by_key(user, key=key)
