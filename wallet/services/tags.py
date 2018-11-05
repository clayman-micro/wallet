from wallet.domain.commands import AddTag
from wallet.domain.entities import Tag
from wallet.domain.specifications import UniqueTagNameSpecification
from wallet.domain.storage import Storage


class AddTagHandler:
    __slots__ = ('_storage', )

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def handle(self, cmd: AddTag) -> None:
        tag = Tag(name=cmd.name, user=cmd.user)

        async with self._storage as store:
            spec = UniqueTagNameSpecification(repo=store.tags)

            satisfied = await spec.is_satisfied_by(tag)
            if satisfied:
                await store.tags.add(tag)
                await store.commit()
