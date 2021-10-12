from asyncio import BaseEventLoop
from datetime import datetime

import pytest
from _pytest.fixtures import FixtureRequest
from databases import Database
from passport.domain import User

from wallet.core.entities.categories import Category
from wallet.storage.categories import categories as categories_table


@pytest.fixture
async def categories(request: FixtureRequest, loop: BaseEventLoop, client, owners: dict[int, User]) -> list[Category]:
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
