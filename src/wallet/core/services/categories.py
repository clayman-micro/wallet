from passport.domain import User

from wallet.core.entities import (
    Category,
    CategoryFilters,
    CategoryPayload,
    CategoryStream,
    OperationFilters,
)
from wallet.core.exceptions import CategoriesNotFound, CategoryAlreadyExist
from wallet.core.services import Service


class CategoryService(Service[Category, CategoryFilters, CategoryPayload]):
    async def add(
        self, payload: CategoryPayload, dry_run: bool = False
    ) -> Category:
        category = Category(name=payload.name, user=payload.user)

        filters = CategoryFilters(user=payload.user, name=payload.name)
        exists = await self._storage.categories.exists(filters=filters)
        if exists:
            raise CategoryAlreadyExist(user=payload.user, category=category)

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

    async def get_or_create(self, filters: CategoryFilters) -> CategoryStream:
        missing_keys = set(filters.keys)
        missing_names = set(filters.names)

        async for category in self._storage.categories.fetch(filters=filters):
            if category.key in missing_keys:
                missing_keys.remove(category.key)

            if category.name in missing_names:
                missing_names.remove(category.name)

            yield category

        if missing_names:
            for name in missing_names:
                payload = CategoryPayload(user=filters.user, name=name)
                category = await self.add(payload)

                yield category

        if missing_keys:
            raise CategoriesNotFound(user=filters.user, keys=missing_keys)

    async def find(self, filters: CategoryFilters) -> CategoryStream:
        async for category in self._storage.categories.fetch(filters=filters):
            yield category

    async def find_by_key(self, user: User, key: int) -> Category:
        return await self._storage.categories.fetch_by_key(user, key=key)
