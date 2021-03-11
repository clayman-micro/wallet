from typing import Set

from passport.domain import User

from wallet.core.entities import (
    AccountFilters,
    CategoryFilters,
    Operation,
    OperationFilters,
    OperationPayload,
    OperationStream,
)
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
        operation.created_on = payload.created_on

        if not dry_run:
            operation.key = await self._storage.operations.save(operation)

        self._logger.info(
            "Add operation", operation=operation.key, dry_run=dry_run,
        )

        return operation

    async def remove(self, entity: Operation, dry_run: bool = False) -> None:
        if not dry_run:
            await self._storage.operations.remove(entity)

        self._logger.info(
            "Remove operation", operation=entity.key, dry_run=dry_run,
        )

    async def find(self, filters: OperationFilters) -> OperationStream:
        account_keys: Set[int] = set()
        category_keys: Set[int] = set()

        dependencies = {}
        operations = {}
        ops_stream = self._storage.operations.fetch(filters=filters)
        async for operation, deps in ops_stream:
            dependencies[operation.key] = deps
            operations[operation.key] = operation

            account_keys.add(deps.account)
            category_keys.add(deps.category)

        accounts = {
            account.key: account
            async for account in self._storage.accounts.fetch(
                filters=AccountFilters(user=filters.user, keys=account_keys)
            )
        }
        categories = {
            category.key: category
            async for category in self._storage.categories.fetch(
                filters=CategoryFilters(user=filters.user, keys=category_keys)
            )
        }

        for operation in operations.values():
            operation.account = accounts[dependencies[operation.key].account]
            operation.category = categories[
                dependencies[operation.key].category
            ]

            yield operation

    async def find_by_key(self, user: User, key: int) -> Operation:
        return await self._storage.operations.fetch_by_key(user, key=key)
