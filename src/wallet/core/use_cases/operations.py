from logging import Logger

from passport.domain import User

from wallet.core.entities import (
    Operation,
    OperationFilters,
    OperationPayload,
    OperationStream,
)
from wallet.core.services.operations import OperationService
from wallet.core.storage import Storage


class OperationUseCase:
    def __init__(self, storage: Storage, logger: Logger) -> None:
        self.storage = storage
        self.service: OperationService = OperationService(
            storage=self.storage, logger=logger
        )

    async def get_by_key(self, user: User, key: int) -> Operation:
        operation = await self.service.find_by_key(user=user, key=key)

        return operation


class AddUseCase(OperationUseCase):
    async def execute(
        self, payload: OperationPayload, dry_run: bool = False
    ) -> Operation:
        operation = await self.service.add(payload=payload, dry_run=dry_run)

        return operation


class SearchUseCase(OperationUseCase):
    async def execute(self, filters: OperationFilters) -> OperationStream:
        async for operation in self.service.find(filters=filters):
            yield operation
