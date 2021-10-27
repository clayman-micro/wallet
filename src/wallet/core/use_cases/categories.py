from logging import Logger
from typing import AsyncIterator

from passport.domain import User

from wallet.core.entities import Category, CategoryFilters, CategoryPayload
from wallet.core.services.categories import CategoryService
from wallet.core.storage import Storage


class CategoryUseCase:
    def __init__(self, storage: Storage, logger: Logger) -> None:
        self.storage = storage
        self.service: CategoryService = CategoryService(storage=self.storage, logger=logger)

    async def get_by_key(self, user: User, key: int) -> Category:
        return self.service.find_by_key(user, key=key)


class AddUseCase(CategoryUseCase):
    async def execute(self, payload: CategoryPayload, dry_run: bool = False) -> Category:
        return await self.service.add(payload=payload, dry_run=dry_run)


class RemoveUseCase(CategoryUseCase):
    async def execute(self, user: User, key: int, dry_run: bool = False) -> None:
        category = await self.get_by_key(user, key=key)

        await self.service.remove(category, dry_run=dry_run)


class SearchUseCase(CategoryUseCase):
    async def execute(self, filters: CategoryFilters) -> AsyncIterator[Category]:
        async for category in self.service.find(filters=filters):
            yield category
