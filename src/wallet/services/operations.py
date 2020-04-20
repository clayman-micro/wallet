from typing import List

from wallet.domain import Account, Operation
from wallet.domain.storage import Storage


class OperationsService:
    __slots = ("_storage",)

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def add_to_account(
        self, account: Account, operation: Operation
    ) -> None:
        operation.account = account

        async with self._storage as store:
            operation.key = await store.operations.add(operation)

            account.apply_operation(operation)

            await store.accounts.update(account, fields=("balance",))
            await store.commit()

    async def remove_from_account(
        self, account: Account, operation: Operation
    ) -> None:
        async with self._storage as store:
            account.rollback_operation(operation)

            await store.accounts.update(account, fields=("balance",))
            removed = await store.operations.remove(operation)

            if removed:
                await store.commit()
            else:
                await store.rollback()

        return removed

    async def fetch(self, account: Account) -> List[Operation]:
        async with self._storage as store:
            operations = await store.operations.find(account)

            tags = await store.tags.find_by_operations(
                account.user, operations=[item.key for item in operations]
            )

            for operation in operations:
                if operation.key in tags:
                    operation.tags = tags[operation.key]

        return operations

    async def fetch_by_key(self, account: Account, key: int) -> Operation:
        async with self._storage as store:
            operation = await store.operations.find_by_key(account, key)

            tags = await store.tags.find_by_operations(
                account.user, operations=(operation.key,)
            )

            if operation.key in tags:
                operation.tags = tags[operation.key]

        return operation
