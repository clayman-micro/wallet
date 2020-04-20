from wallet.domain import Tag, User
from wallet.domain.storage import EntityAlreadyExist, Storage


class TagsService:
    __slots__ = ("_storage",)

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def add(self, name: str, user: User) -> Tag:
        tag = Tag(key=0, name=name, user=user)

        async with self._storage as store:
            existed = await store.tags.find_by_name(user, name)

            if existed:
                raise EntityAlreadyExist()

            tag.key = await store.tags.add(tag)
            await store.commit()

        return tag
