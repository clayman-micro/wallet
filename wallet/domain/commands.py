from datetime import datetime
from decimal import Decimal
from typing import NamedTuple, Optional

from wallet.domain.entities import Account, Operation, OperationType, Tag, User


class RegisterAccount(NamedTuple):
    name: str
    user: User


class RenameAccount(NamedTuple):
    name: str
    account: Account


class RemoveAccount(NamedTuple):
    account: Account


class AddTag(NamedTuple):
    name: str
    user: User


class RemoveTag(NamedTuple):
    tag: Tag


class AddOperationToAccount(NamedTuple):
    amount: Decimal
    account: Account
    type: OperationType = OperationType.expense
    description: Optional[str] = None
    created_on: Optional[datetime] = None


class ChangeOperationAmount(NamedTuple):
    amount: Decimal
    operation: Operation


class ChangeOperationType(NamedTuple):
    type: OperationType
    operation: Operation


class ChangeOperationDate(NamedTuple):
    create_on: datetime
    operation: Operation
