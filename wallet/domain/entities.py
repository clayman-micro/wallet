from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, List

import attr
import pendulum  # type: ignore


@attr.s(auto_attribs=True, slots=True)
class User:
    key: int
    email: str


class UserProvider:
    async def identify(self, token: str) -> User:
        raise NotImplementedError


@attr.s(slots=True)
class Balance:
    rest: Decimal = attr.ib(default=Decimal("0"))
    expenses: Decimal = attr.ib(default=Decimal("0"))
    incomes: Decimal = attr.ib(default=Decimal("0"))
    month: date = attr.ib(factory=lambda: pendulum.today().start_of("month"))


@attr.s(auto_attribs=True, slots=True)
class Account:
    key: int
    name: str
    user: User
    balance: List[Any] = []

    def __attrs_post_init__(self):
        if not self.balance:
            month = pendulum.today().start_of("month").date()

            self.balance = [Balance(month=month)]

    def apply_operation(self, operation: "Operation") -> None:
        month = pendulum.date(
            year=operation.created_on.year, month=operation.created_on.month, day=1
        )

        balance = {item.month: item for item in self.balance}

        today = pendulum.today().date()
        months = {month, today, *balance.keys()}
        first, last = min(months), max(months)

        result = []

        rest = Decimal("0")
        current = first
        while current <= last:
            if current not in balance:
                balance[current] = Balance(rest=rest, month=current)
            else:
                rest = balance[current].rest

            if current == month:
                if operation.type == OperationType.expense:
                    balance[current].expenses += operation.amount
                elif operation.type == OperationType.income:
                    balance[current].incomes += operation.amount

            if current >= month:
                if operation.type == OperationType.expense:
                    balance[current].rest -= operation.amount
                elif operation.type == OperationType.income:
                    balance[current].rest += operation.amount

            result.append(balance[current])
            current = current.add(months=1)

        self.balance = result

    def rollback_operation(self, operation: "Operation"):
        month = pendulum.date(
            year=operation.created_on.year, month=operation.created_on.month, day=1
        )

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
class Tag:
    key: int
    name: str
    user: User


class OperationType(Enum):
    expense = "expense"
    income = "income"


@attr.s(auto_attribs=True, slots=True)
class Operation:
    key: int
    amount: Decimal
    account: Account
    description: str = attr.ib(default="")
    type: OperationType = attr.ib(default=OperationType.expense)
    tags: List[Tag] = attr.ib(default=attr.Factory(set))
    created_on: datetime = attr.ib(factory=lambda: datetime.now())
