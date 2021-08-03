import abc
from typing import AsyncGenerator, Generic, TypeVar

from passport.domain import User

from wallet.core.entities.abc import Entity, Filters


E = TypeVar("E", bound=Entity)
F = TypeVar("F", bound=Filters)


class Repo(Generic[E, F], metaclass=abc.ABCMeta):
    async def fetch(self, filters: F) -> AsyncGenerator[E, None]:
        pass

    async def fetch_by_key(self, user: User, key: int) -> E:
        pass

    async def exists(self, filters: F) -> bool:
        pass

    async def save(self, entity: E) -> int:
        pass

    async def remove(self, entity: E) -> bool:
        pass
