from datetime import datetime
from typing import Dict, List

from wallet.entities import (Account, EntityAlreadyExist, Operation,
                             OperationType, Tag)
from wallet.repositories.operations import OperationsRepo
from wallet.validation import Validator, ValidationError


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
    def __init__(self, repo: OperationsRepo) -> None:
        self.account = None
        self.repo = repo
        self.filters = None

    def set_params(self, account: Account, filters=None) -> None:
        self.account = account
        self.filters = filters

    async def execute(self) -> List[Operation]:
        if self.filters and self.filters.year and self.filters.month:
            year, month = self.filters.year, self.filters.month
        else:
            now = datetime.now()
            year, month = now.year, now.month

        return await self.repo.fetch(account=self.account, year=int(year),
                                     month=int(month))


class GetOperationInteractor(object):
    def __init__(self, repo: OperationsRepo) -> None:
        self.repo = repo
        self.account = None
        self.pk = 0

    def set_params(self, account: Account, pk: int) -> None:
        self.account = account
        self.pk = pk

    async def execute(self) -> Operation:
        return await self.repo.fetch_operation(self.account, self.pk)


class CreateOperationInteractor(object):
    def __init__(self, accounts_repo, operations_repo: OperationsRepo) -> None:
        self.accounts_repo = accounts_repo
        self.operations_repo = operations_repo

        self.account: Account = None
        self.payload: Dict = {}

        self.validator = Validator(schema)

    def set_params(self, account: Account, payload: Dict) -> None:
        self.account = account
        self.payload = payload

    async def execute(self) -> Operation:
        self.payload.setdefault('type', OperationType.EXPENSE.value.lower())
        self.payload.setdefault('created_on', datetime.now())

        document = self.validator.validate_payload(self.payload)

        operation = Operation.from_dict({**document, 'account': self.account})
        operation.pk = await self.operations_repo.save(operation)

        self.account.apply_operation(operation)
        await self.accounts_repo.update(self.account, ['amount'])

        return operation


class UpdateOperationInteractor(object):
    def __init__(self, accounts_repo, operations_repo: OperationsRepo) -> None:
        self.accounts_repo = accounts_repo
        self.operations_repo = operations_repo

        self.pk = 0
        self.account = None
        self.payload = {}

        self.validator = Validator(schema)

    def set_params(self, account: Account, pk: int, payload: Dict) -> None:
        self.account = account
        self.pk = pk
        self.payload = payload

    async def execute(self) -> bool:
        operation = await self.operations_repo.fetch_operation(
            self.account, self.pk
        )

        update_account = False

        document = self.validator.validate_payload(self.payload, True)
        if 'created_on' not in self.payload:
            document.pop('created_on')

        for key, value in iter(document.items()):
            if key == 'amount' or key == 'type':
                self.account.rollback_operation(operation)

            setattr(operation, key, value)

            if key == 'amount' or key == 'type':
                self.account.apply_operation(operation)
                update_account = True

        if update_account:
            await self.accounts_repo.update(self.account, ['amount'])

        await self.operations_repo.update(operation, list(document.keys()))
        return operation


class RemoveOperationInteractor(object):
    def __init__(self, accounts_repo, operations_repo: OperationsRepo) -> None:
        self.accounts_repo = accounts_repo
        self.operations_repo = operations_repo

        self.pk = 0
        self.account = None

    def set_params(self, account: Account, pk: int) -> None:
        self.account = account
        self.pk = pk

    async def execute(self) -> bool:
        operation = await self.operations_repo.fetch_operation(
            self.account, self.pk
        )

        self.account.rollback_operation(operation)
        await self.accounts_repo.update(self.account, ('amount', ))

        removed = await self.operations_repo.remove(operation)
        return removed


class OperationAddTagInteractor(object):
    def __init__(self, operations_repo, tags_repo) -> None:
        self.operations_repo = operations_repo
        self.tags_repo = tags_repo

        self.operation = None  # type: Operation
        self.tag_name = ''

    def set_params(self, operation: Operation, tag_name: str) -> None:
        self.operation = operation
        self.tag_name = tag_name

    async def execute(self) -> bool:
        tags = await self.tags_repo.fetch(self.operation.account.owner,
                                          name=self.tag_name)

        if tags:
            tag = tags[0]
        else:
            tag = Tag(self.tag_name, self.operation.account.owner)
            tag.pk = await self.tags_repo.save_tag(tag)

        try:
            await self.operations_repo.save_tag(self.operation, tag)
        except EntityAlreadyExist:
            raise ValidationError(errors={'tag': 'Already exists'})

        return tag
