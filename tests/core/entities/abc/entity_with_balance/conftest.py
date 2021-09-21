from datetime import date, datetime
from decimal import Decimal

import pytest
from _pytest.fixtures import FixtureRequest

from wallet.core.entities.abc import Balance, EntityWithBalance, OperationType


@pytest.fixture(scope="function")
def entity() -> EntityWithBalance:
    return EntityWithBalance()


@pytest.fixture(scope="function")
def amount(request: FixtureRequest) -> Decimal:
    return Decimal(request.param)


@pytest.fixture(scope="function")
def operation_type(request: FixtureRequest) -> OperationType:
    return OperationType[request.param]


@pytest.fixture(scope="function")
def created_on(request: FixtureRequest, today: datetime) -> datetime:
    return today.add(months=request.param)


def prepare_balance(raw: dict[str, str], month: date) -> dict[date, Balance]:
    balance = {}

    for item in raw:
        key = month.add(months=item.get("month_offset", 0))

        balance[key] = Balance(
            month=key,
            rest=Decimal(item.get("rest", "0.0")),
            expenses=Decimal(item.get("expenses", "0.0")),
            incomes=Decimal(item.get("incomes", "0.0")),
        )

    return balance


@pytest.fixture(scope="function")
def balance(request: FixtureRequest, month: date) -> dict[date, Balance]:
    return prepare_balance(request.param, month)


@pytest.fixture(scope="function")
def expected(request: FixtureRequest, month: date) -> dict[date, Balance]:
    return prepare_balance(request.param, month)
