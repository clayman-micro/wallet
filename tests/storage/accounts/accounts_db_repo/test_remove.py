import pytest
import sqlalchemy
from aiohttp import web
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
async def test_success(client: web.Application, accounts: list[Account], account: Account, expected: int) -> None:
    """Successfully remove account from storage."""
    database = client.app["db"]
    repo = AccountDBRepo(database=database)

    result = await repo.remove(account)

    assert result is True
    query = (
        sqlalchemy.select([sqlalchemy.func.count(accounts_table.c.id)])
        .select_from(accounts_table)
        .where(
            sqlalchemy.and_(accounts_table.c.user == account.user.key, accounts_table.c.enabled == True)  # noqa: E712
        )
    )
    count = await database.fetch_val(query=query)
    assert count == expected


@pytest.mark.integration
async def test_failed(client: web.Application, owner: User, accounts: list[Account]) -> None:
    """Could not remove not existed account from storage."""
    account = Account(name="Visa Classic", user=owner)
    repo = AccountDBRepo(database=client.app["db"])

    with pytest.raises(AccountNotFound):
        await repo.remove(account)
