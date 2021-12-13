from passport.domain import User

from wallet.core.entities import Category, CategoryFilters
from wallet.core.storage.abc import Repo


class CategoryRepo(Repo[Category, CategoryFilters]):
    """Repository to get access to Categories storage."""

    async def fetch_by_name(self, user: User, name: str) -> Category:
        """Fetch category from storage by name.

        Args:
            user: Category owner instance.
            name: Category name.

        Returns:
            Category instance.
        """
