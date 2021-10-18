import pytest
import sqlalchemy
from passport.domain import User

from wallet.core.entities.categories import Category
from wallet.core.exceptions import CategoryNotFound
from wallet.storage.categories import categories as categories_table
from wallet.storage.categories import CategoryDBRepo


@pytest.fixture
def category(request, owner: User, categories: list[Category]) -> Category:
    """Get category instance."""
    for category in categories:
        if category.key == request.param:
            return category

    raise CategoryNotFound(owner, name="")


@pytest.mark.integration
async def test_success(
    client, repo: CategoryDBRepo, categories: list[Category], category: Category, expected: int
) -> None:
    """Successfully remove category from storage."""

    result = await repo.remove(category)

    assert result is True
    query = (
        sqlalchemy.select([sqlalchemy.func.count(categories_table.c.id)])
        .select_from(categories_table)
        .where(
            sqlalchemy.and_(
                categories_table.c.user == category.user.key, categories_table.c.enabled == True  # noqa: E712
            )
        )
    )
    count = await client.app["db"].fetch_val(query=query)
    assert count == expected


@pytest.mark.integration
async def test_failed(repo: CategoryDBRepo, owner: User, categories: list[Category]) -> None:
    """Could not remove not existed category from storage."""
    category = Category(name="Visa Classic", user=owner)

    with pytest.raises(CategoryNotFound):
        await repo.remove(category)
