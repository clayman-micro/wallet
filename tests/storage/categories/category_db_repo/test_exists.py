import pytest
from aiohttp import web
from passport.domain import User

from wallet.core.entities.categories import Category, CategoryFilters
from wallet.storage.categories import CategoryDBRepo


@pytest.mark.integration
async def test_success(
    client: web.Application, owner: User, name: str, categories: list[Category], expected: list[Category]
) -> None:
    """Successfully fetch categories from storage."""
    repo = CategoryDBRepo(database=client.app["db"])

    result = await repo.exists(filters=CategoryFilters(user=owner, name=name))

    assert result == expected
