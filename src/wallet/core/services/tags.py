from typing import AsyncGenerator

from passport.domain import User

from wallet.core.entities import (
    OperationFilters,
    Tag,
    TagFilters,
    TagPayload,
)
from wallet.core.exceptions import EntityAlreadyExist
from wallet.core.services import Service


class TagService(Service[Tag, TagFilters, TagPayload]):
    async def add(self, payload: TagPayload, dry_run: bool = False) -> Tag:
        tag = Tag(name=payload.name, user=payload.user)

        exists = await self._storage.tags.fetch_by_name(user=tag.user, name=tag.name)
        if exists:
            raise EntityAlreadyExist()

        if not dry_run:
            tag.key = await self._storage.tags.save(tag)

        self._logger.info(
            "Add new tag", user=tag.user.key, name=tag.name, dry_run=dry_run,
        )

        return tag

    async def remove(self, entity: Tag, dry_run: bool = False) -> None:
        filters = OperationFilters(user=entity.user, tags=[entity])
        has_operations = await self._storage.operations.exists(filters)
        if has_operations:
            raise Exception

        if not dry_run:
            await self._storage.tags.remove(entity=entity)

        self._logger.info(
            "Remove tag", user=entity.user.key, name=entity.name, dry_run=dry_run,
        )

    async def find(self, filters: TagFilters) -> AsyncGenerator[Tag, None]:
        return await self._storage.tags.fetch(filters=filters)

    async def find_by_key(self, user: User, key: int) -> Tag:
        return await self._storage.tags.fetch_by_key(user, key=key)
