from logging import Logger
from typing import AsyncGenerator, Generic, TypeVar

from passport.domain import User

from wallet.core.entities import Entity, Filters, Payload
from wallet.core.storage import Storage


E = TypeVar("E", bound=Entity)
F = TypeVar("F", bound=Filters)
P = TypeVar("P", bound=Payload)


class Service(Generic[E, F, P]):
    def __init__(self, storage: Storage, logger: Logger) -> None:
        self._storage = storage
        self._logger = logger

    async def add(self, payload: P, dry_run: bool = False) -> E:
        raise NotImplementedError()

    async def remove(self, entity: E, dry_run: bool = False) -> None:
        raise NotImplementedError()

    async def find(self, filters: F) -> AsyncGenerator[E, None]:
        raise NotImplementedError()

    async def find_by_key(self, user: User, key: int) -> E:
        raise NotImplementedError()
