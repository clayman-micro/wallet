from decimal import Decimal

import pytest

from tests.conftest import load_test_cases
from wallet.core.entities import Balance, EntityWithBalance, OperationType


def load_test_case(request, today, month):
    def load_balance(raw):
        for item in raw:
            key = month.add(months=item.get("month_offset", 0))

            yield key, Balance(
                month=key,
                rest=Decimal(item.get("rest", "0.0")),
                expenses=Decimal(item.get("expenses", "0.0")),
                incomes=Decimal(item.get("incomes", "0.0")),
            )

    return {
        "amount": Decimal(request.param.get("amount")),
        "operation_type": OperationType(request.param.get("operation_type")),
        "created_on": today.add(months=request.param.get("month_offset", 0)),
        "balance": {key: value for key, value in load_balance(request.param.get("balance", []))},
        "expected": {key: value for key, value in load_balance(request.param.get("expected"))},
    }


@pytest.fixture(params=load_test_cases(__file__, "add_operation.json"))
def add_operation_test_case(request, today, month):
    return load_test_case(request, today, month)


@pytest.mark.unit
def test_update_balance_after_add_operation(add_operation_test_case):
    entity = EntityWithBalance()
    if add_operation_test_case.get("balance"):
        entity.balance = add_operation_test_case.get("balance")

    entity.add_operation(
        amount=add_operation_test_case.get("amount"),
        operation_type=add_operation_test_case.get("operation_type"),
        created_on=add_operation_test_case.get("created_on"),
    )

    assert entity.balance == add_operation_test_case.get("expected")


@pytest.fixture(params=load_test_cases(__file__, "drop_operation.json"))
def drop_operation_test_case(request, today, month):
    return load_test_case(request, today, month)


@pytest.mark.unit
def test_update_balance_after_drop_operation(drop_operation_test_case):
    entity = EntityWithBalance()

    if drop_operation_test_case.get("balance"):
        entity.balance = drop_operation_test_case.get("balance")

    entity.drop_operation(
        amount=drop_operation_test_case.get("amount"),
        operation_type=drop_operation_test_case.get("operation_type"),
        created_on=drop_operation_test_case.get("created_on"),
    )

    assert entity.balance == drop_operation_test_case.get("expected")
