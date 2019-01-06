from wallet.domain import EntityAlreadyExist
from wallet.domain.entities import Tag, User
from wallet.domain.storage import Storage, TagQuery
from wallet.validation import Validator


class TagValidator(Validator):
    def __init__(self, *args, **kwargs) -> None:
        schema = {
            'name': {'required': True, 'empty': False, 'type': 'string'}
        }

        super(TagValidator, self).__init__(schema, *args, **kwargs)


class TagsService:
    __slots__ = ('_storage', )

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def add(self, name: str, user: User) -> Tag:
        tag = Tag(key=0, name=name, user=user)

        async with self._storage as store:
            query = TagQuery(user=user, name=name)
            existed = await store.tags.find(query)

            if existed:
                raise EntityAlreadyExist()

            tag.key = await store.tags.add(tag)
            await store.commit()

        return tag
