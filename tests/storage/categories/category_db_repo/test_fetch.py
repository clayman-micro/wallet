import pytest
from _pytest.fixtures import FixtureRequest
from aiohttp import web
from passport.domain import User

from wallet.core.entities.categories import Category, CategoryFilters
from wallet.storage.categories import CategoryDBRepo


@pytest.fixture
def expected(request: FixtureRequest, owners: dict[int, User]) -> list[Category]:
    """Prepare expected result."""
    entities: list[Category] = []
    for item in request.param:
        owner = owners.get(item["owner"])
        category = Category(name=item["name"], user=owner)
        category.key = item.get("key", 0)

        entities.append(category)

    return entities


@pytest.mark.integration
async def test_success(
    client: web.Application, owner: User, categories: list[Category], expected: list[Category]
) -> None:
    """Successfully fetch categories from storage."""
    repo = CategoryDBRepo(database=client.app["db"])

    result = [account async for account in repo.fetch(filters=CategoryFilters(user=owner))]

    assert result == expected