import pytest
import sqlalchemy
from passport.domain import User

from wallet.core.entities.accounts import Account
from wallet.core.exceptions import AccountNotFound
from wallet.storage.accounts import AccountDBRepo
from wallet.storage.accounts import accounts as accounts_table


@pytest.fixture
def account(request, owner: User, accounts: list[Account]) -> Account:
    """Get account instance."""
    for account in accounts:
        if account.key == request.param:
            return account

    raise AccountNotFound(owner, name="")


@pytest.mark.integration
async def test_success(client, repo: AccountDBRepo, accounts: list[Account], account: Account, expected: int) -> None:
    """Successfully remove account from storage."""
    result = await repo.remove(account)

    assert result is True
    query = (
        sqlalchemy.select([sqlalchemy.func.count(accounts_table.c.id)])
        .select_from(accounts_table)
        .where(
            sqlalchemy.and_(accounts_table.c.user == account.user.key, accounts_table.c.enabled == True)  # noqa: E712
        )
    )
    count = await client.app["db"].fetch_val(query=query)
    assert count == expected


@pytest.mark.integration
async def test_failed(repo: AccountDBRepo, owner: User, accounts: list[Account]) -> None:
    """Could not remove not existed account from storage."""
    account = Account(name="Visa Classic", user=owner)

    with pytest.raises(AccountNotFound):
        await repo.remove(account)
