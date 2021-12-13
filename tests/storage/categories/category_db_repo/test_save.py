import pytest
from passport.domain import User

from wallet.core.entities.categories import Category
from wallet.core.exceptions import CategoryAlreadyExist
from wallet.storage.categories import CategoryDBRepo


@pytest.mark.integration
async def test_success(
    repo: CategoryDBRepo, owner: User, name: str, categories: list[Category], expected: list[Category]
) -> None:
    """Successfully add new category to storage."""
    category = Category(name=name, user=owner)

    result = await repo.save(category)

    assert result == expected


@pytest.mark.integration
async def test_failed(repo: CategoryDBRepo, owner: User, name: str, categories: list[Category]) -> None:
    """Unable to add new category to storage."""
    category = Category(name=name, user=owner)

    with pytest.raises(CategoryAlreadyExist):
        await repo.save(category)
