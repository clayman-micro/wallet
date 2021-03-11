from passport.domain import User

from wallet.core.entities import Category, CategoryFilters
from wallet.core.storage.base import Repo


class CategoryRepo(Repo[Category, CategoryFilters]):
    async def fetch_by_name(self, user: User, name: str) -> Category:
        pass
