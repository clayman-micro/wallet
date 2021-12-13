from abc import abstractmethod

from passport.domain import User

from wallet.core.entities import Account, AccountFilters
from wallet.core.storage.abc import Repo


class AccountRepo(Repo[Account, AccountFilters]):
    """Repository to get access to Accounts storage."""

    @abstractmethod
    async def fetch_by_name(self, user: User, name: str) -> Account:
        """Fetch account by it's name.

        Args:
            user: Account owner instance.
            name: Account name.

        Returns:
            Account instance.
        """
