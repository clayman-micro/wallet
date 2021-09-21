import abc

from passport.domain import User

from wallet.core.entities import Account, AccountFilters
from wallet.core.storage.abc import Repo


class AccountRepo(Repo[Account, AccountFilters]):
    @abc.abstractmethod
    async def fetch_by_name(self, user: User, name: str) -> Account:
        pass
