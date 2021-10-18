import pytest
from passport.domain import User

from wallet.core.entities.accounts import Account, AccountFilters
from wallet.storage.accounts import AccountDBRepo


@pytest.mark.integration
async def test_success(
    repo: AccountDBRepo, owner: User, name: str, accounts: list[Account], expected: list[Account]
) -> None:
    """Successfully fetch accounts from storage."""
    result = await repo.exists(filters=AccountFilters(user=owner, name=name))

    assert result == expected
