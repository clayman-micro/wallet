import pytest
from passport.domain import User

from wallet.core.entities.accounts import Account
from wallet.core.exceptions import AccountNotFound
from wallet.storage.accounts import AccountDBRepo


@pytest.fixture
def expected(request, owners: dict[int, User]) -> Account:
    """Prepare expected result."""
    owner = owners.get(request.param["owner"])
    account = Account(name=request.param["name"], user=owner)
    account.key = request.param.get("key", 0)

    return account


@pytest.mark.integration
async def test_success(repo: AccountDBRepo, owner: User, name: str, accounts: list[Account], expected: Account) -> None:
    """Successfully fetch account from storage by key."""
    result = await repo.fetch_by_name(user=owner, name=name)

    assert result == expected


@pytest.mark.integration
async def test_missing(repo: AccountDBRepo, owner: User, name: str, accounts: list[Account]) -> None:
    """Fetch missing account from storage by key."""
    with pytest.raises(AccountNotFound):
        await repo.fetch_by_name(user=owner, name=name)
