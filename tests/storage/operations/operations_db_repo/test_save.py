from datetime import datetime
from decimal import Decimal

import pytest
from passport.domain import User

from wallet.core.entities import Account, Category, Operation, OperationType
from wallet.storage.operations import OperationDBRepo


@pytest.fixture
def operation(request, owner: User, accounts: list[Account], categories: list[Category]) -> Operation:
    accounts_map = {account.key: account for account in accounts}
    categories_map = {category.key: category for category in categories}

    operation = Operation(
        amount=Decimal(request.param["amount"]),
        description=request.param["description"],
        user=owner,
        account=accounts_map[request.param["account"]],
        category=categories_map[request.param["category"]],
        operation_type=OperationType(request.param["type"]),
    )
    operation.created_on = datetime.strptime(request.param["created_on"], "%Y-%m-%dT%H:%M:%S")

    return operation


@pytest.mark.inregration
async def test_success(repo: OperationDBRepo, owner: User, operation: Operation, expected: Operation) -> None:
    """Successfully add new operation."""
    result = await repo.save(operation)

    assert result == expected
