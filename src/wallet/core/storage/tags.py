from passport.domain import User

from wallet.core.entities import Tag, TagFilters
from wallet.core.storage.abc import Repo


class TagRepo(Repo[Tag, TagFilters]):
    """Repository to get access to Tags storage."""

    async def fetch_by_name(self, user: User, name: str) -> Tag:
        """Fetch tag from storage by name.

        Args:
            user: Tag owner instance.
            name: Tag name.

        Returns:
            Tag instance.
        """
