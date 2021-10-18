import pytest
from passport.domain import User

from wallet.core.entities.accounts import Account, AccountFilters
from wallet.storage.accounts import AccountDBRepo


@pytest.fixture
def expected(request, owners: dict[int, User]) -> list[Account]:
    """Prepare expected result."""
    entities: list[Account] = []
    for item in request.param:
        owner = owners.get(item["owner"])
        account = Account(name=item["name"], user=owner)
        account.key = item.get("key", 0)

        entities.append(account)

    return entities


@pytest.mark.integration
async def test_success(repo: AccountDBRepo, owner: User, accounts: list[Account], expected: list[Account]) -> None:
    """Successfully fetch accounts from storage."""
    result = [account async for account in repo.fetch(filters=AccountFilters(user=owner))]

    assert result == expected
