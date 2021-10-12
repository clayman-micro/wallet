import pytest
from aiohttp import web
from passport.domain import User

from wallet.core.entities.categories import Category
from wallet.core.exceptions import CategoryAlreadyExist
from wallet.storage.categories import CategoryDBRepo


@pytest.mark.integration
async def test_success(
    client: web.Application, owner: User, name: str, categories: list[Category], expected: list[Category]
) -> None:
    """Successfully add new category to storage."""
    category = Category(name=name, user=owner)
    repo = CategoryDBRepo(database=client.app["db"])

    result = await repo.save(category)

    assert result == expected


@pytest.mark.integration
async def test_failed(client: web.Application, owner: User, name: str, categories: list[Category]) -> None:
    """Unable to add new category to storage."""
    category = Category(name=name, user=owner)
    repo = CategoryDBRepo(database=client.app["db"])

    with pytest.raises(CategoryAlreadyExist):
        await repo.save(category)
