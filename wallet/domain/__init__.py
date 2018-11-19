from typing import Generic, List, Optional, TypeVar


class EntityNotFound(Exception):
    pass


class EntityAlreadyExist(Exception):
    pass


E = TypeVar('E')
Q = TypeVar('Q')


class Query:
    __slots__ = ('key', )

    def __init__(self, key: Optional[int] = None):
        self.key = key


class Repo(Generic[E, Q]):
    async def find(self, query: Q) -> List[E]:
        raise NotImplementedError

    async def add(self, instance: E) -> int:
        raise NotImplementedError

    async def update(self, instance: E) -> bool:
        raise NotImplementedError

    async def remove(self, instance: E) -> bool:
        raise NotImplementedError


class UnitOfWork:
    async def __aenter__(self):
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    async def commit(self):
        raise NotImplementedError

    async def rollback(self):
        raise NotImplementedError
