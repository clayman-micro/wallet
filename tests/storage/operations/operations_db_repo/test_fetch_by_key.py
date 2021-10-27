from datetime import datetime
from decimal import Decimal

import pytest
from passport.domain import User

from wallet.core.entities import Operation, OperationType
from wallet.core.exceptions import OperationNotFound
from wallet.storage.operations import OperationDBRepo


@pytest.fixture
def expected(request, owner: User):
    operation = Operation(
        amount=Decimal(request.param["amount"]),
        description=request.param["description"],
        user=owner,
        account=None,
        category=None,
        operation_type=OperationType(request.param["type"]),
    )
    operation.key = request.param["key"]
    operation.created_on = datetime.strptime(request.param["created_on"], "%Y-%m-%dT%H:%M:%S")

    return operation


@pytest.mark.integration
async def test_success(
    repo: OperationDBRepo, owner: User, operations: list[Operation], key: int, expected: Operation
) -> None:
    result = await repo.fetch_by_key(user=owner, key=key)

    assert result == expected


@pytest.mark.integration
async def test_missing(repo: OperationDBRepo, owner: User, key: int, operations: list[Operation]) -> None:
    """Fetch missing operation from storage by key."""
    with pytest.raises(OperationNotFound):
        await repo.fetch_by_key(user=owner, key=key)
