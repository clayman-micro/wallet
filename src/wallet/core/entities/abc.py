from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List

import pendulum  # type: ignore
from passport.domain import User

from wallet.core.tools import month_range


@dataclass
class Entity:
    key: int = field(default=0, init=False)

    def __post_init__(self):
        pass


@dataclass
class Payload:
    user: User


@dataclass
class Filters:
    user: User
    keys: List[int] = field(default_factory=list)


@dataclass
class Period:
    beginning: date
    ending: date


@dataclass
class Balance(Entity):
    month: date
    expenses: Decimal = field(default=Decimal("0.0"))
    incomes: Decimal = field(default=Decimal("0.0"))
    rest: Decimal = field(default=Decimal("0.0"))


class OperationType(Enum):
    income = "income"
    expense = "expense"


@dataclass
class EntityWithBalance(Entity):
    balance: Dict[date, Balance] = field(default_factory=dict, init=False)

    def __post_init__(self):
        super().__post_init__()

        if not self.balance:
            month = pendulum.today().start_of("month").date()

            self.balance[month] = Balance(month=month)

    def add_operation(self, amount: Decimal, operation_type: OperationType, created_on: datetime) -> None:
        operation_month = pendulum.instance(created_on).start_of("month").date()

        rest = None
        for month in month_range(operation_month):
            if month in self.balance:
                balance = self.balance[month]
            else:
                balance = Balance(month=month)

            if rest is None:
                rest = balance.rest

            if month == operation_month:
                if operation_type == OperationType.expense:
                    balance.expenses += amount
                elif operation_type == OperationType.income:
                    balance.incomes += amount

            rest = rest + balance.incomes - balance.expenses
            balance.rest = rest

            self.balance[month] = balance

    def drop_operation(self, amount: Decimal, operation_type: OperationType, created_on: datetime) -> None:
        operation_month = pendulum.instance(created_on).start_of("month").date()

        rest = None
        for month in month_range(operation_month):
            if month in self.balance:
                balance = self.balance[month]
            else:
                balance = Balance(month=month)

            if rest is None:
                rest = balance.rest

            if month == operation_month:
                if operation_type == OperationType.expense:
                    balance.expenses -= amount
                    rest += amount
                elif operation_type == OperationType.income:
                    balance.incomes -= amount
                    rest -= amount

            rest = rest + balance.incomes - balance.expenses
            balance.rest = rest

            self.balance[month] = balance
