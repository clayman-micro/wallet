from abc import abstractmethod
from typing import Generic, List, TypeVar

from passport.domain import User

from wallet.core.entities.abc import EntityType, FiltersType


class Repo(Generic[EntityType, FiltersType]):
    @abstractmethod
    def fetch(self, filters: FiltersType) -> List[EntityType]:
        """Fetch entities from storage.

        Args:
            filters: Params to filter entities.

        Returns:
            Entity instances from storage.
        """

    @abstractmethod
    async def fetch_by_key(self, user: User, key: int) -> EntityType:
        """Fetch entity by key.

        Args:
            user: Entity owner.
            key: Entity identifier.

        Returns:
            Entity instance.
        """

    @abstractmethod
    async def exists(self, filters: FiltersType) -> bool:
        """Check if entities exist in storage.

        Args:
            filters: Params to filter entities.

        Returns:
            Entities exist in storage.
        """

    @abstractmethod
    async def save(self, entity: EntityType) -> None:
        """Save entity changes to storage.

        Args:
            entity: Entity instance.
        """

    @abstractmethod
    async def remove(self, entity: EntityType) -> bool:
        """Remove entity from storage.

        Args:
            entity: Entity instance.
        """


RepoType = TypeVar("RepoType", bound=Repo)
