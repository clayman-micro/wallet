from datetime import datetime
from typing import Any

import pytest
from databases import Database
from passport.domain import User

from wallet.core.entities.accounts import Account
from wallet.core.entities.categories import Category
from wallet.storage.accounts import accounts as accounts_table
from wallet.storage.categories import categories as categories_table


@pytest.fixture(scope="module")
def owners(request, faker) -> dict[int, User]:
    """Prepare owners."""
    users: dict[int, User] = {}

    for item in request.param:
        user = User(key=item["key"], email=item.get("email", faker.free_email()))
        users[user.key] = user

    return users


@pytest.fixture(scope="function")
def owner(request, owners: dict[int, User]) -> User:
    """Choose owner."""
    return owners.get(request.param)


@pytest.fixture
async def accounts(request, loop, client, owners: dict[int, User]) -> list[Account]:
    """Prepare accounts in storage."""
    database: Database = client.app["db"]
    query = accounts_table.insert().returning(accounts_table.c.id)

    entities: list[Account] = []
    for item in request.param:
        owner = owners.get(item["owner"])
        account = Account(name=item["name"], user=owner)
        account.key = await database.execute(
            query,
            values={
                "name": account.name,
                "user": account.user.key,
                "enabled": item.get("enabled", False),
                "created_on": datetime.now(),
            },
        )

        entities.append(account)

    return entities


@pytest.fixture
async def categories(request, loop, client, owners: dict[int, User]) -> list[Category]:
    """Prepare categories in storage."""
    database: Database = client.app["db"]
    query = categories_table.insert().returning(categories_table.c.id)

    entities: list[Category] = []
    for item in request.param:
        owner = owners.get(item["owner"])
        category = Category(name=item["name"], user=owner)
        category.key = await database.execute(
            query,
            values={
                "name": category.name,
                "user": category.user.key,
                "enabled": item.get("enabled", False),
                "created_on": datetime.now(),
            },
        )

        entities.append(category)

    return entities


@pytest.fixture
def key(request) -> int:
    """Get instance key."""
    return request.param


@pytest.fixture
def name(request) -> str:
    """Get instance name."""
    return request.param


@pytest.fixture
def expected(request) -> Any:
    """Get expected test result."""
    return request.param
