from decimal import Decimal
from typing import List, Optional

from wallet.entities import Account, Owner
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
        self._repo: AccountsRepository = repo
        self._name: str = ''
        self._owner: Optional[Owner] = None

    def set_params(self, owner: Owner, name: str = '') -> None:
        self._owner = owner
        self._name = name

    async def execute(self) -> List[Account]:
        return await self._repo.fetch(owner=self._owner, name=self._name)


class GetAccountInteractor(object):
    def __init__(self, repo: AccountsRepository) -> None:
        self._repo: AccountsRepository = repo
        self._pk: int = 0
        self._owner: Optional[Owner] = None

    def set_params(self, owner: Owner, pk: int) -> None:
        self._owner = owner
        self._pk = pk

    async def execute(self) -> Account:
        return await self._repo.fetch_by_pk(owner=self._owner, pk=self._pk)


class CreateAccountInteractor(object):
    """
    Create account

    Primary course:
    1. Validate incoming data
    2. Create account instance if data is valid
    3. Save account instance to repository
    4. Return account instance

    """
    def __init__(self, repo: AccountsRepository) -> None:
        self._repo: AccountsRepository = repo
        self._owner: Optional[Owner] = None
        self._name = ''
        self._amount: Decimal = Decimal(0.0)

        self._validator = Validator(schema)

    def set_params(self, owner: Owner, name: str, amount: Decimal) -> None:
        self._owner = owner
        self._name = name
        self._amount = amount

    async def execute(self) -> Account:
        # Validate incoming data
        document = self._validator.validate_payload({
            'name': self._name,
            'amount': self._amount,
            'original': self._amount
        })

        exists = await self._repo.check_exists(self._owner, document['name'])
        if exists:
            raise ValidationError({'name': 'Already exist'})

        account = Account.from_dict({**document, 'owner': self._owner})
        account.pk = await self._repo.save(account)

        return account


class UpdateAccountInteractor(object):
    def __init__(self, repo: AccountsRepository, operations_repo) -> None:
        self.repo: AccountsRepository = repo
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
        account = await self.repo.fetch_by_pk(self.owner, self.pk)

        fields = {}

        for field in ('name', 'original'):
            value = getattr(self, field, None)
            if value:
                fields[field] = value

        document = self.validator.validate_payload(fields, True)

        for key, value in iter(document.items()):
            setattr(account, key, value)

        if self.original and self.original != account.original:
            operations = await self.operation_repo.fetch(account)

            for operation in operations:
                account.apply_operation(operation)

            document['amount'] = account.amount

        await self.repo.update(account, **document)
        return account


class RemoveAccountInteractor(object):
    def __init__(self, repo: AccountsRepository) -> None:
        self._repo: AccountsRepository = repo
        self._owner: Optional[Owner] = None
        self._pk: int = 0

    def set_params(self, owner: Owner, pk: int) -> None:
        self._owner = owner
        self._pk = pk

    async def execute(self) -> bool:
        account = await self._repo.fetch_by_pk(self._owner, self._pk)
        removed = await self._repo.remove(account)
        return removed
