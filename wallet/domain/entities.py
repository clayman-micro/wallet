from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, List, Optional

import attr
import pendulum

from wallet.domain import Entity


@attr.s(auto_attribs=True, slots=True)
class User(Entity):
    email: str
    key: Optional[int] = 0


@attr.s(slots=True)
class Balance:
    rest: Decimal = attr.ib(default=Decimal('0'))
    expenses: Decimal = attr.ib(default=Decimal('0'))
    incomes: Decimal = attr.ib(default=Decimal('0'))
    month: date = attr.ib(factory=lambda: pendulum.today().start_of('month'))


@attr.s(auto_attribs=True, slots=True)
class Account(Entity):
    name: str
    user: User
    key: Optional[int] = 0
    balance: List[Any] = []

    def __attrs_post_init__(self):
        if not self.balance:
            month = pendulum.today().start_of('month').date()

            self.balance = [Balance(month=month)]

    def apply_operation(self, operation: 'Operation') -> None:
        month = pendulum.date(year=operation.created_on.year,
                              month=operation.created_on.month, day=1)

        balance = {item.month: item for item in self.balance}

        today = pendulum.today().date()
        first, last = min(balance.keys()), max(balance.keys())
        first = min(first, month)
        last = max((last, month, today))

        result = []

        rest = 0
        current = first
        while current <= last:
            item = balance.get(current, Balance(rest=rest, month=current))

            if current == month:
                if operation.type == OperationType.expense:
                    item.expenses += operation.amount
                elif operation.type == OperationType.income:
                    item.incomes += operation.amount

            if current >= month:
                if operation.type == OperationType.expense:
                    item.rest -= operation.amount
                elif operation.type == OperationType.income:
                    item.rest += operation.amount

            result.append(item)
            current = current.add(months=1)

        self.balance = result

    def rollback_operation(self, operation: 'Operation'):
        month = pendulum.date(year=operation.created_on.year,
                              month=operation.created_on.month, day=1)

        balance = sorted(self.balance, key=lambda item: item.month)

        for item in balance:
            if item.month == month:
                if operation.type == OperationType.expense:
                    item.expenses -= operation.amount
                elif operation.type == OperationType.income:
                    item.incomes -= operation.amount

            if item.month >= month:
                if operation.type == OperationType.expense:
                    item.rest += operation.amount
                elif operation.type == OperationType.income:
                    item.rest -= operation.amount

        self.balance = balance


@attr.s(auto_attribs=True, slots=True)
class Tag(Entity):
    name: str
    user: User
    key: Optional[int] = 0


class OperationType(Enum):
    expense = 'expense'
    income = 'income'


@attr.s(auto_attribs=True, slots=True)
class Operation(Entity):
    amount: Decimal
    account: Account
    key: int = attr.ib(default=0)
    description: str = attr.ib(default='')
    type: OperationType = attr.ib(default=OperationType.expense)
    tags: List[Tag] = attr.ib(default=attr.Factory(set))
    created_on: Optional[datetime] = attr.ib(factory=lambda: datetime.now())
