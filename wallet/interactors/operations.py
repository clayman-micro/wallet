from decimal import Decimal
from typing import List, Optional

from wallet.entities import Account, Operation, OperationType
from wallet.validation import Validator


schema = {
    'amount': {
        'type': 'decimal',
        'coerce': 'decimal',
        'required': True
    },
    'type': {
        'type': 'operation_type',
        'coerce': 'operation_type',
        'required': True
    },
    'description': {
        'type': 'string',
        'maxlength': 255,
        'empty': True
    },
    'created_on': {
        'type': 'datetime',
        'coerce': 'datetime',
        'default_setter': 'utcnow'
    }
}


class GetOperationsInteractor(object):
    def __init__(self, repo) -> None:
        self.account: Optional[Account] = None
        self.repo = repo

    def set_params(self, account: Account) -> None:
        self.account = account

    async def execute(self) -> List[Operation]:
        return await self.repo.fetch(account=self.account)


class GetOperationInteractor(object):
    def __init__(self, repo) -> None:
        self.repo = repo
        self.account: Optional[Account] = None
        self.pk: int = 0

    def set_params(self, account: Account, pk: int) -> None:
        self.account = account
        self.pk = pk

    async def execute(self) -> Operation:
        return await self.repo.fetch_by_pk(account=self.account, pk=self.pk)


class CreateOperationInteractor(object):
    def __init__(self, accounts_repo, operations_repo) -> None:
        self.accounts_repo = accounts_repo
        self.operations_repo = operations_repo

        self.amount: Decimal = Decimal(0.0)
        self.type: OperationType = OperationType.EXPENSE
        self.account: Account = None
        self.description: str = ''

        self.validator = Validator(schema)

    def set_params(self, amount: Decimal, account: Account,
                   operation_type: OperationType, description: str='') -> None:

        self.amount = amount
        self.account = account
        self.type = operation_type
        self.description = description

    async def execute(self) -> Operation:
        document = self.validator.validate_payload({
            'amount': self.amount,
            'type': self.type,
            'description': self.description
        })

        operation = Operation.from_dict({**document, 'account': self.account})
        operation.pk = await self.operations_repo.save(operation)

        self.account.apply_operation(operation)
        await self.accounts_repo.update(self.account,
                                        amount=self.account.amount)

        return operation


class UpdateOperationInteractor(object):
    def __init__(self, accounts_repo, operations_repo) -> None:
        self.accounts_repo = accounts_repo
        self.operations_repo = operations_repo

        self.pk = 0
        self.account: Account = None

        self.validator = Validator(schema)

    def set_params(self, account: Account, pk: int, amount: Decimal = None,
                   type: OperationType = None, description: str = None,
                   created_on: str = None) -> None:

        self.account = account
        self.pk = pk
        self.amount = amount
        self.type = type
        self.description = description
        self.created_on = created_on

    async def execute(self) -> bool:
        operation = await self.operations_repo.fetch_by_pk(
            self.account, self.pk
        )

        fields = {}
        update_account = False

        for field in ('amount', 'type', 'description', 'created_on'):
            value = getattr(self, field, None)
            if value:
                fields[field] = value

        document = self.validator.validate_payload(fields, True)
        if not self.created_on:
            document.pop('created_on')

        for key, value in iter(document.items()):
            if key == 'amount' or key == 'type':
                self.account.rollback_operation(operation)

            setattr(operation, key, value)

            if key == 'amount' or key == 'type':
                self.account.apply_operation(operation)
                update_account = True

        if update_account:
            await self.accounts_repo.update(self.account,
                                            amount=self.account.amount)

        updated = await self.operations_repo.update(operation, **document)
        return updated


class RemoveOperationInteractor(object):
    def __init__(self, accounts_repo, operations_repo) -> None:
        self.accounts_repo = accounts_repo
        self.operations_repo = operations_repo

        self.pk = 0
        self.account: Account = None

    def set_params(self, account: Account, pk: int) -> None:
        self.account = account
        self.pk = pk

    async def execute(self) -> bool:
        operation = await self.operations_repo.fetch_by_pk(
            self.account, self.pk
        )

        self.account.rollback_operation(operation)
        await self.accounts_repo.update(self.account,
                                        amount=self.account.amount)

        removed = await self.operations_repo.remove(operation)
        return removed
