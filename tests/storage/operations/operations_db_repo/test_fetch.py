from datetime import datetime
from decimal import Decimal

import pytest
from passport.domain import User

from wallet.core.entities import Operation, OperationDependencies, OperationFilters, OperationType
from wallet.storage.operations import OperationDBRepo


@pytest.fixture
def filters(request, owners: dict[int, User]) -> OperationFilters:
    """Prepare filters to fetch operations."""
    filters = OperationFilters(user=owners[request.param["owner"]])

    return filters


@pytest.fixture
def expected(request, owners: dict[int, User]) -> tuple[list[Operation], dict[int, OperationDependencies]]:
    """Prepare expected result."""
    entities: list[Operation] = []
    dependencies: dict[int, OperationDependencies] = {}

    for item in request.param:
        owner = owners.get(item["owner"])

        operation = Operation(
            amount=Decimal(item["amount"]),
            description=item["description"],
            user=owner,
            account=None,
            category=None,
            operation_type=OperationType(item["type"]),
        )
        operation.key = item["key"]
        operation.created_on = datetime.strptime(item["created_on"], "%Y-%m-%dT%H:%M:%S")

        entities.append(operation)
        dependencies[operation.key] = OperationDependencies(**item["deps"])

    return entities, dependencies


async def test_success(
    repo: OperationDBRepo, filters: OperationFilters, operations: list[Operation], expected: list[Operation]
) -> None:
    """Successfully fetch operations without filters."""
    dependencies = {}
    operations = []

    async for operation, deps in repo.fetch(filters=filters):  # act
        operations.append(operation)
        dependencies[operation.key] = deps

    expected_operations, expected_dependencies = expected
    assert operations == expected_operations
    assert dependencies == expected_dependencies
