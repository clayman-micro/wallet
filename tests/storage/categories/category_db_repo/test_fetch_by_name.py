import pytest
from _pytest.fixtures import FixtureRequest
from aiohttp import web
from passport.domain import User

from wallet.core.entities.categories import Category
from wallet.core.exceptions import CategoryNotFound
from wallet.storage.categories import CategoryDBRepo


@pytest.fixture
def expected(request: FixtureRequest, owners: dict[int, User]) -> Category:
    """Prepare expected result."""
    owner = owners.get(request.param["owner"])
    category = Category(name=request.param["name"], user=owner)
    category.key = request.param.get("key", 0)

    return category


@pytest.mark.integration
async def test_success(
    client: web.Application, owner: User, name: str, categories: list[Category], expected: Category
) -> None:
    """Successfully fetch category from storage by key."""
    repo = CategoryDBRepo(database=client.app["db"])

    result = await repo.fetch_by_name(user=owner, name=name)

    assert result == expected


@pytest.mark.integration
async def test_missing(client: web.Application, owner: User, name: str, categories: list[Category]) -> None:
    """Fetch missing category from storage by key."""
    repo = CategoryDBRepo(database=client.app["db"])

    with pytest.raises(CategoryNotFound):
        await repo.fetch_by_name(user=owner, name=name)
