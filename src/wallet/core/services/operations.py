from typing import AsyncIterator, Dict, Set

from passport.domain import User

from wallet.core.entities import (
    Account,
    AccountFilters,
    Category,
    CategoryFilters,
    Operation,
    OperationFilters,
    OperationPayload,
)
from wallet.core.entities.operations import BulkOperationsPayload, OperationStream
from wallet.core.exceptions import CategoriesNotFound, UnprocessableOperations
from wallet.core.services import Service


class OperationService(Service[Operation, OperationFilters, OperationPayload]):
    async def create(
        self, payload: OperationPayload, account: Account, category: Category, dry_run: bool = False,
    ) -> Operation:
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

        return operation

    async def add(self, payload: OperationPayload, dry_run: bool = False) -> Operation:
        account = await self._storage.accounts.fetch_by_key(user=payload.user, key=payload.account)
        category = await self._storage.categories.fetch_by_key(user=payload.user, key=payload.category)

        operation = await self.create(payload, account, category, dry_run=dry_run)

        self._logger.info(
            "Add operation", operation=operation.key, dry_run=dry_run,
        )

        return operation

    async def add_bulk(
        self,
        payload: BulkOperationsPayload,
        account_stream: AsyncIterator[Account],
        category_stream: AsyncIterator[Category],
        dry_run: bool = False,
    ) -> OperationStream:
        accounts = {account.key: account async for account in account_stream}

        category_by_key: Dict[int, Category] = {}
        category_by_name: Dict[str, Category] = {}

        try:
            async for category in category_stream:
                category_by_key[category.key] = category
                category_by_name[category.name] = category
        except CategoriesNotFound:
            pass

        unprocessable_operations = []

        for item in payload.operations:
            account = accounts.get(item.account, None)

            if not account:
                unprocessable_operations.append(item)
                continue

            category = None
            if isinstance(item.category, int):
                category = category_by_key.get(item.category, None)
            elif isinstance(item.category, str):
                category = category_by_name.get(item.category, None)

            if not category:
                unprocessable_operations.append(item)
                continue

            operation = await self.create(item, account, category, dry_run=dry_run)

            self._logger.info(
                "Add operation", operation=operation.key, bulk=True, dry_run=dry_run,
            )

            yield operation

        if unprocessable_operations:
            raise UnprocessableOperations(user=payload.user, operations=unprocessable_operations)

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
            operation.category = categories[dependencies[operation.key].category]

            yield operation

    async def find_by_key(self, user: User, key: int) -> Operation:
        return await self._storage.operations.fetch_by_key(user, key=key)
