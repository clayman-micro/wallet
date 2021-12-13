import pytest
from passport.domain import User

from wallet.core.entities.categories import Category, CategoryFilters
from wallet.storage.categories import CategoryDBRepo


@pytest.mark.integration
async def test_success(
    repo: CategoryDBRepo, owner: User, name: str, categories: list[Category], expected: list[Category]
) -> None:
    """Successfully fetch categories from storage."""
    result = await repo.exists(filters=CategoryFilters(user=owner, name=name))

    assert result == expected
