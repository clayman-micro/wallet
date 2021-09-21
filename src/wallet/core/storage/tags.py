import abc

from passport.domain import User

from wallet.core.entities import Tag, TagFilters
from wallet.core.storage.abc import Repo


class TagRepo(Repo[Tag, TagFilters]):
    @abc.abstractmethod
    async def fetch_by_name(self, user: User, name: str) -> Tag:
        pass
