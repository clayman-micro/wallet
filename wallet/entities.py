from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, Set


class EntityNotFound(Exception):
    pass


class EntityAlreadyExist(Exception):
    pass


class UnknownOperationType(Exception):
    pass


class OperationType(Enum):
    INCOME = 'income'
    EXPENSE = 'expense'


class Entity(object):
    def __init__(self, pk: int = 0, enabled: bool = True,
                 created_on: datetime = None) -> None:

        self.pk = pk
        self.enabled = enabled

        if not created_on:
            created_on = datetime.utcnow()

        self.created_on = created_on


class Owner(Entity):
    def __init__(self, email: str, **optional) -> None:
        self.email = email

        super(Owner, self).__init__(**optional)


class Tag(Entity):
    def __init__(self, name: str, owner: Owner, **optional) -> None:
        self.name = name
        self.owner = owner

        super(Tag, self).__init__(**optional)


class Account(Entity):
    def __init__(self, name: str, amount: Decimal, owner: Owner, **opt) -> None:
        self.name = name
        self.amount = amount
        self.owner = owner
        self.original = opt.pop('original', Decimal(0.0))

        super(Account, self).__init__(**opt)

    @classmethod
    def from_dict(self, props: Dict) -> 'Account':
        return Account(
            props['name'], props['amount'], props['owner'],
            original=props.get('original', Decimal(0.0)), pk=props.get('pk', 0),
            enabled=props.get('enabled', True),
            created_on=props.get('created_on', None)
        )

    def apply_operation(self, operation: 'Operation') -> None:
        if operation.account.pk and operation.account.pk != self.pk:
            raise ValueError('Could not apply operation')

        if operation.type == OperationType.EXPENSE:
            self.amount -= operation.amount
        elif operation.type == OperationType.INCOME:
            self.amount += operation.amount
        else:
            raise UnknownOperationType()

    def rollback_operation(self, operation: 'Operation') -> None:
        if operation.account.pk and operation.account.pk != self.pk:
            raise ValueError('Could not rollback operation')

        if operation.type == OperationType.EXPENSE:
            self.amount += operation.amount
        elif operation.type == OperationType.INCOME:
            self.amount -= operation.amount
        else:
            raise ValueError()


class Operation(Entity):
    def __init__(self, amount: Decimal, account: Account, **optional) -> None:
        self.amount = amount
        self.account = account

        self._tags: Set[Tag] = set()

        self.type = optional.pop('type', OperationType.EXPENSE)
        self.description = optional.pop('description', '')

        super(Operation, self).__init__(**optional)

    @classmethod
    def from_dict(cls, props: Dict) -> 'Operation':
        return Operation(
            props['amount'], props['account'], pk=props.get('pk', 0),
            type=props.get('type', OperationType.EXPENSE),
            description=props.get('description', ''),
            enabled=props.get('enabled', True),
            created_on=props.get('created_on', None)
        )

    @property
    def tags(self) -> Set[Tag]:
        return self._tags

    def add_tag(self, tag: Tag) -> None:
        self._tags.add(tag)

    def remove_tag(self, tag: Tag) -> None:
        self._tags.remove
