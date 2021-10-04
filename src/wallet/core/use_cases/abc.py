from abc import abstractmethod
from logging import Logger
from typing import Any, Generic, TypeVar

from wallet.core.registry import Registry


ResultType = TypeVar("ResultType")


class UseCase(Generic[ResultType]):
    registry: Registry
    logger: Logger

    def __init__(self, registry: Registry, logger: Logger) -> None:
        self.registry = registry
        self.logger = logger

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ResultType:
        ...
