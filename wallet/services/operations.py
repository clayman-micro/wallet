from datetime import datetime
from decimal import Decimal
from typing import Optional

from wallet.domain.entities import Account, Operation, OperationType
from wallet.domain.storage import Storage
from wallet.validation import Validator


class OperationValidator(Validator):
    def __init__(self, *args, **kwargs) -> None:
        schema = {
            "amount": {"required": True, "type": "decimal", "coerce": "decimal"},
            "type": {
                "type": "operation_type",
                "coerce": "operation_type",
                "default_setter": "expense",
            },
            "description": {"type": "string", "maxlength": 255, "empty": True},
            "created_on": {
                "type": "datetime",
                "coerce": "datetime",
                "default_setter": "utcnow",
            },
        }

        super(OperationValidator, self).__init__(schema, *args, **kwargs)

    def _validate_type_operation_type(self, value):
        if value and isinstance(value, OperationType):
            return True

    def _normalize_coerce_operation_type(self, value):
        if value:
            return OperationType(value)

    def _normalize_default_setter_expense(self, document):
        return OperationType.expense


class OperationsService:
    __slots = ("_storage",)

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def add_to_account(
        self,
        account: Account,
        amount: Decimal,
        description: str = "",
        operation_type: Optional[OperationType] = None,
        created_on: Optional[datetime] = None,
    ) -> Operation:

        if not operation_type:
            operation_type = OperationType.expense

        if not created_on:
            created_on = datetime.now()

        operation = Operation(
            key=0,
            amount=amount,
            account=account,
            description=description,
            type=operation_type,
            created_on=created_on,
        )

        async with self._storage as store:
            operation.key = await store.operations.add(operation)

            account.apply_operation(operation)

            await store.accounts.update(account, fields=("balance",))
            await store.commit()

        return operation

    async def remove_from_account(self, account: Account, operation: Operation) -> None:
        async with self._storage as store:
            account.rollback_operation(operation)

            await store.accounts.update(account, fields=("balance",))
            removed = await store.operations.remove(operation)

            if removed:
                await store.commit()
            else:
                await store.rollback()

        return removed
