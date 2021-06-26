from passport.domain import User

from wallet.core.entities import Account, AccountFilters
from wallet.core.storage.base import Repo


class AccountRepo(Repo[Account, AccountFilters]):
    async def fetch_by_name(self, user: User, name: str) -> Account:
        pass
