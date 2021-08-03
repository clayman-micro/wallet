from logging import Logger

from passport.domain import User

from wallet.core.entities import (
    AccountFilters,
    CategoryFilters,
    Operation,
    OperationFilters,
    OperationPayload,
    OperationStream,
)
from wallet.core.entities.operations import BulkOperationsPayload
from wallet.core.services.accounts import AccountService
from wallet.core.services.categories import CategoryService
from wallet.core.services.operations import OperationService
from wallet.core.storage import Storage


class OperationUseCase:
    def __init__(self, storage: Storage, logger: Logger) -> None:
        self.storage = storage
        self.service: OperationService = OperationService(storage=self.storage, logger=logger)

    async def get_by_key(self, user: User, key: int) -> Operation:
        operation = await self.service.find_by_key(user=user, key=key)

        return operation


class AddUseCase(OperationUseCase):
    async def execute(self, payload: OperationPayload, dry_run: bool = False) -> Operation:
        operation = await self.service.add(payload=payload, dry_run=dry_run)

        return operation


class AddBulkUseCase(OperationUseCase):
    def __init__(self, storage: Storage, logger: Logger) -> None:
        super().__init__(storage=storage, logger=logger)

        self.accounts: AccountService = AccountService(storage, logger)
        self.categories: CategoryService = CategoryService(storage, logger)

    async def execute(self, payload: BulkOperationsPayload, dry_run: bool = False) -> OperationStream:
        account_stream = self.accounts.find(filters=AccountFilters(user=payload.user, keys=payload.account_keys))

        category_stream = self.categories.get_or_create(
            CategoryFilters(user=payload.user, keys=payload.category_keys, names=payload.category_names,)
        )

        stream = self.service.add_bulk(
            payload=payload, account_stream=account_stream, category_stream=category_stream, dry_run=dry_run,
        )

        async for operation in stream:
            yield operation


class SearchUseCase(OperationUseCase):
    async def execute(self, filters: OperationFilters) -> OperationStream:
        async for operation in self.service.find(filters=filters):
            yield operation
