from decimal import Decimal
from typing import List, Optional

from wallet.entities import Account, EntityAlreadyExist, Owner
from wallet.repositories.accounts import AccountsRepository
from wallet.validation import ValidationError, Validator


schema = {
    'name': {
        'type': 'string',
        'maxlength': 255,
        'required': True,
        'empty': False
    },
    'amount': {
        'type': 'decimal',
        'coerce': 'decimal',
        'empty': True
    },
    'original': {
        'type': 'decimal',
        'coerce': 'decimal',
        'empty': True
    }
}


class GetAccountsInteractor(object):
    def __init__(self, repo: AccountsRepository) -> None:
        self._repo = repo
        self._name = ''
        self._owner = None

    def set_params(self, owner: Owner, name: str = '') -> None:
        self._owner = owner
        self._name = name

    async def execute(self) -> List[Account]:
        return await self._repo.fetch(owner=self._owner, name=self._name)


class GetAccountInteractor(object):
    def __init__(self, repo: AccountsRepository) -> None:
        self._repo = repo
        self._pk = 0
        self._owner = None

    def set_params(self, owner: Owner, pk: int) -> None:
        self._owner = owner
        self._pk = pk

    async def execute(self) -> Account:
        return await self._repo.fetch_account(owner=self._owner, pk=self._pk)


class CreateAccountInteractor(object):
    def __init__(self, repo: AccountsRepository) -> None:
        self._repo = repo
        self._owner = None
        self._name = ''
        self._amount = Decimal(0.0)

        self._validator = Validator(schema)

    def set_params(self, owner: Owner, name: str, amount: Decimal) -> None:
        self._owner = owner
        self._name = name
        self._amount = amount

    async def execute(self) -> Account:
        document = self._validator.validate_payload({
            'name': self._name,
            'amount': self._amount,
            'original': self._amount
        })

        try:
            account = Account.from_dict({**document, 'owner': self._owner})
            account.pk = await self._repo.save(account)
        except EntityAlreadyExist:
            raise ValidationError({'name': 'Already exist'})

        return account


class UpdateAccountInteractor(object):
    def __init__(self, repo: AccountsRepository, operations_repo) -> None:
        self.repo = repo
        self.operation_repo = operations_repo
        self.pk = 0

        self.validator = Validator(schema)

    def set_params(self, owner: Owner, pk: int, name: str = None,
                   original: Decimal = None) -> None:

        self.owner = owner
        self.pk = pk
        self.name = name
        self.original = original

    async def execute(self) -> bool:
        account = await self.repo.fetch_account(self.owner, self.pk)

        fields = {}

        for field in ('name', 'original'):
            value = getattr(self, field, None)
            if value:
                fields[field] = value

        document = self.validator.validate_payload(fields, True)

        for key, value in iter(document.items()):
            setattr(account, key, value)

        keys = list(document.keys())
        if self.original and self.original != account.original:
            account.amount = document['original']

            operations = await self.operation_repo.fetch_operations(account)

            for operation in operations:
                account.apply_operation(operation)

            document['amount'] = account.amount
            keys.append('amount')

        await self.repo.update(account, keys)
        return account


class RemoveAccountInteractor(object):
    def __init__(self, repo: AccountsRepository) -> None:
        self._repo = repo
        self._owner = None
        self._pk = 0

    def set_params(self, owner: Owner, pk: int) -> None:
        self._owner = owner
        self._pk = pk

    async def execute(self) -> bool:
        account = await self._repo.fetch_account(self._owner, self._pk)
        removed = await self._repo.remove(account)
        return removed
