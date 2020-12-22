from typing import AsyncGenerator

from passport.domain import User

from wallet.core.entities import Operation, OperationFilters, OperationPayload
from wallet.core.services import Service


class OperationService(Service[Operation, OperationFilters, OperationPayload]):
    async def add(
        self, payload: OperationPayload, dry_run: bool = False
    ) -> Operation:
        account = await self._storage.accounts.fetch_by_key(
            user=payload.user, key=payload.account
        )

        category = await self._storage.categories.fetch_by_key(
            user=payload.user, key=payload.category
        )

        operation = Operation(
            amount=payload.amount,
            description=payload.description,
            account=account,
            category=category,
            operation_type=payload.operation_type,
            user=payload.user,
        )

        if not dry_run:
            operation.key = await self._storage.operations.save(operation)

        self._logger.info(
            "Add operation",
            user=payload.user,
            operation=operation.key,
            dry_run=dry_run,
        )

        return operation

    async def remove(self, entity: Operation, dry_run: bool = False) -> None:
        if not dry_run:
            await self._storage.operations.remove(entity)

        self._logger.info(
            "Remove operation",
            user=entity.user,
            operation=entity.key,
            dry_run=dry_run,
        )

    async def find(
        self, filters: OperationFilters
    ) -> AsyncGenerator[Operation, None]:
        return await self._storage.operations.fetch(filters=filters)

    async def find_by_key(self, user: User, key: int) -> Operation:
        return await self._storage.operations.fetch_by_key(user, key=key)
