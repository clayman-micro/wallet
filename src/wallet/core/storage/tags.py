from passport.domain import User

from wallet.core.entities import Tag, TagFilters
from wallet.core.storage.base import Repo


class TagRepo(Repo[Tag, TagFilters]):
    async def fetch_by_name(self, user: User, name: str) -> Tag:
        pass
