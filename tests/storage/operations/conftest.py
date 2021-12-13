from datetime import datetime
from decimal import Decimal

import pytest
from databases import Database
from passport.domain import User

from wallet.core.entities import Account, Category, Operation, OperationType
from wallet.storage.operations import OperationDBRepo
from wallet.storage.operations import operations as ops_table


@pytest.fixture
async def operations(
    request, loop, client, owners: dict[int, User], accounts: list[Account], categories: list[Category]
) -> list[Operation]:
    """Prepare operations in storage."""
    database: Database = client.app["db"]

    accounts_map = {account.key: account for account in accounts}
    categories_map = {category.key: category for category in categories}

    query = ops_table.insert().returning(ops_table.c.id)

    entities: list[Operation] = []
    for item in request.param:
        owner = owners.get(item["owner"])

        operation = Operation(
            amount=Decimal(item["amount"]),
            description=item["description"],
            user=owner,
            account=accounts_map[item["account"]],
            category=categories_map[item["category"]],
            operation_type=OperationType(item["type"]),
        )
        operation.created_on = datetime.strptime(item["created_on"], "%Y-%m-%dT%H:%M:%S")
        operation.key = await database.execute(
            query,
            values={
                "amount": operation.amount,
                "desc": operation.description,
                "type": operation.operation_type.value,
                "user": operation.user.key,
                "account_id": operation.account.key,
                "category_id": operation.category.key,
                "enabled": item.get("enabled", False),
                "created_on": operation.created_on,
            },
        )

        entities.append(operation)

    return entities


@pytest.fixture
def repo(client) -> OperationDBRepo:
    return OperationDBRepo(database=client.app["db"])
