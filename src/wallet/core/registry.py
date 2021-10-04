from abc import abstractmethod
from logging import Logger
from typing import Generic, List, Protocol, Type, TypeVar

from passport.domain import User

from wallet.core.entities.abc import EntityType, FiltersType


class RegistryError(Exception):
    _name: str

    def __init__(self, name: str, *args: object) -> None:
        super().__init__(*args)
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class RepositoryNotFound(RegistryError):
    """Repository not found in registry."""


class RepositoryAlreadyExist(RegistryError):
    """Repository already exist in registry."""


class ServiceNotFound(RegistryError):
    """Service not found in registry."""


class Repo(Protocol):
    async def fetch(self, filters: FiltersType) -> List[EntityType]:
        ...

    async def fetch_by_key(self, user: User, key: int) -> EntityType:
        ...

    async def exists(self, filters: FiltersType) -> bool:
        ...

    async def save(self, entity: EntityType) -> int:
        ...

    async def remove(self, entity: EntityType) -> bool:
        ...


RepoType = TypeVar("RepoType")


class Service(Protocol):
    """Base service protocol."""

    @classmethod
    def create_service(self, registry: "Registry") -> "Service":
        """Create new service instance.

        Args:
            registry: App registry instance.

        Returns:
            New service instaince.
        """


class Registry(Generic[RepoType]):
    logger: Logger
    repositories: dict[str, RepoType]
    services: dict[str, Type[Service]]

    def get_service(self, name: str) -> Service:
        """Get service instance from registry.

        Args:
            name: Service name.
            logger: Logger instance.

        Returns:
            Service instance.
        """
        try:
            service_cls = self.services[name]
        except KeyError:
            raise ServiceNotFound(name=name)

        return service_cls.create_service(registry=self)

    def get_repository(self, name: str) -> RepoType:
        """Ger repository instance from registry.

        Args:
            name: Repository name.

        Returns:
            Repository instance.
        """
        try:
            return self.repositories[name]
        except KeyError:
            raise RepositoryNotFound(name=name)

    @abstractmethod
    def register_repository(self, name: str, repo_cls: Type[RepoType]) -> None:
        """Register new repository in registry.

        Args:
            name: Repository name.
            repo_cls: New repository class.
        """
