from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import AsyncGenerator, Iterable, List, Optional, Tuple, Union

from passport.domain import User

from wallet.core.entities.abc import Entity, Filters, OperationType, Payload
from wallet.core.entities.accounts import Account
from wallet.core.entities.categories import Category
from wallet.core.entities.tags import Tag


@dataclass
class Operation(Entity):
    amount: Decimal
    description: str
    user: User
    account: Optional[Account] = None
    category: Optional[Category] = None
    operation_type: OperationType = OperationType.expense
    tags: List[Tag] = field(default_factory=list)
    created_on: datetime = field(init=False)


@dataclass
class OperationDependencies:
    account: int
    category: int


OperationStream = AsyncGenerator[Tuple[Operation, OperationDependencies], None]


@dataclass
class OperationFilters(Filters):
    month: Optional[date] = None
    account: Optional[Account] = None
    category: Optional[Category] = None
    tags: List[Tag] = field(default_factory=list)


@dataclass
class OperationPayload(Payload):
    amount: Decimal
    account: int
    category: Union[int, str]
    operation_type: OperationType
    created_on: datetime
    description: str = ""
    tags: List[int] = field(default_factory=list)


@dataclass
class BulkOperationsPayload(Payload):
    account_keys: Iterable[int]
    category_keys: Iterable[int]
    category_names: Iterable[str]
    operations: List[OperationPayload]
