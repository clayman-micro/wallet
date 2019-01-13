from typing import Dict, Iterable, List

from wallet.domain import Tag, User


class TagsRepo:
    async def find(self, user: User) -> List[Tag]:
        raise NotImplementedError

    async def find_by_key(self, user: User, key: int) -> Tag:
        raise NotImplementedError

    async def find_by_name(self, user: User, name: str) -> List[Tag]:
        raise NotImplementedError

    async def find_by_operations(self, user: User, operations: Iterable[int]) -> Dict[int, List[Tag]]:
        raise NotImplementedError

    async def add(self, tag: Tag) -> int:
        raise NotImplementedError

    async def update(self, tag: Tag, fields: Iterable[str]) -> bool:
        raise NotImplementedError

    async def remove(self, tag: Tag) -> bool:
        raise NotImplementedError
