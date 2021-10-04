from abc import abstractmethod
from typing import Generic, List

from passport.domain import User

from wallet.core.entities.abc import EntityType, FiltersType, PayloadType
from wallet.core.registry import Registry


class Service(Generic[EntityType, FiltersType, PayloadType]):
    @abstractmethod
    @classmethod
    def create_service(self, registry: Registry) -> "Service":
        ...

    @abstractmethod
    async def add(self, payload: PayloadType, dry_run: bool = False) -> EntityType:
        ...

    @abstractmethod
    async def remove(self, entity: EntityType, dry_run: bool = False) -> None:
        ...

    @abstractmethod
    async def find(self, filters: FiltersType) -> List[EntityType]:
        ...

    @abstractmethod
    async def find_by_key(self, user: User, key: int) -> EntityType:
        ...
