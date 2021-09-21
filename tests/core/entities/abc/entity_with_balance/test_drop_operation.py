from datetime import date, datetime
from decimal import Decimal

import pytest

from wallet.core.entities.abc import Balance, EntityWithBalance, OperationType


@pytest.mark.unit
def test_success(
    entity: EntityWithBalance,
    amount: Decimal,
    operation_type: OperationType,
    created_on: datetime,
    balance: dict[date, Balance],
    expected: dict[date, Balance],
) -> None:
    """Successfully drop operation from entity with balance."""
    entity.balance = balance

    entity.drop_operation(amount=amount, operation_type=operation_type, created_on=created_on)  # act

    assert entity.balance == expected
