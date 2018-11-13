from wallet.domain import EntityAlreadyExist, Repo, Specification
from wallet.domain.entities import Account, Tag
from wallet.domain.storage import AccountQuery, TagQuery


class UniqueAccountNameSpecification(Specification[Account]):
    __slots__ = ('_repo', )

    def __init__(self, repo: Repo) -> None:
        self._repo = repo

    async def is_satisfied_by(self, instance: Account) -> bool:
        query = AccountQuery(user=instance.user, name=instance.name)

        accounts = await self._repo.find(query)
        if accounts:
            raise EntityAlreadyExist()

        return True


class UniqueTagNameSpecification(Specification[Tag]):
    __slots__ = ('_repo', )

    def __init__(self, repo: Repo) -> None:
        self._repo = repo

    async def is_satisfied_by(self, instance: Tag) -> bool:
        query = TagQuery(user=instance.user, name=instance.name)

        tags = await self._repo.find(query)
        if tags:
            raise EntityAlreadyExist

        return True
