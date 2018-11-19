from datetime import datetime
from decimal import Decimal
from typing import Optional

from wallet.domain.entities import Account, Operation, OperationType
from wallet.domain.storage import Storage


class OperationsService:
    __slots = ('_storage', )

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def add_to_account(self, account: Account, amount: Decimal,
                             description: str = '',
                             operation_type: Optional[OperationType] = None,
                             created_on: Optional[datetime] = None) -> Operation:

        if not operation_type:
            operation_type = OperationType.expense

        if not created_on:
            created_on = datetime.now()

        operation = Operation(key=0, amount=amount, account=account,
                              description=description, type=operation_type,
                              created_on=created_on)

        async with self._storage as store:
            operation.key = await store.operations.add(operation)

            account.apply_operation(operation)

            await store.accounts.update(account, balance=account.balance)
            await store.commit()

        return operation
