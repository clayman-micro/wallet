from typing import List, Optional


class Entity:
    pass


class EntityNotFound(Exception):
    pass


class EntityAlreadyExist(Exception):
    pass


class Specification:
    def is_satisfied_by(self, instance: Entity) -> bool:
        raise NotImplementedError


class Query:
    __slots__ = ('key', )

    def __init__(self, key: Optional[int] = None):
        self.key = key


class Repository:
    async def find(self, query: Query) -> List[Entity]:
        raise NotImplementedError

    async def add(self, instance: Entity) -> int:
        raise NotImplementedError


class UnitOfWork:
    async def __aenter__(self):
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError
