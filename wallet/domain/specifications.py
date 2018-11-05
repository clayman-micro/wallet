from wallet.domain import EntityAlreadyExist, Specification
from wallet.domain.entities import Account, Tag
from wallet.domain.storage import AccountQuery, AccountsRepo, TagQuery, TagsRepo


class UniqueAccountNameSpecification(Specification):
    __slots__ = ('_repo', )

    def __init__(self, repo: AccountsRepo) -> None:
        self._repo = repo

    async def is_satisfied_by(self, instance: Account) -> bool:
        query = AccountQuery(user=instance.user, name=instance.name)

        accounts = await self._repo.find(query)
        if accounts:
            raise EntityAlreadyExist()

        return True


class UniqueTagNameSpecification(Specification):
    __slots__ = ('_repo', )

    def __init__(self, repo: TagsRepo) -> None:
        self._repo = repo

    async def is_satisfied_by(self, instance: Tag) -> bool:
        query = TagQuery(user=instance.user, name=instance.name)

        tags = await self._repo.find(query)
        if tags:
            raise EntityAlreadyExist

        return True
