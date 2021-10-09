import pytest
from aiohttp import web
from passport.domain import User

from wallet.core.entities.accounts import Account
from wallet.core.exceptions import AccountAlreadyExist
from wallet.storage.accounts import AccountDBRepo


@pytest.mark.integration
async def test_success(
    client: web.Application, owner: User, name: str, accounts: list[Account], expected: list[Account]
) -> None:
    """Successfully fetch accounts from storage."""
    account = Account(name=name, user=owner)
    repo = AccountDBRepo(database=client.app["db"])

    result = await repo.save(account)

    assert result == expected


@pytest.mark.integration
async def test_failed(client: web.Application, owner: User, name: str, accounts: list[Account]) -> None:
    """Successfully fetch accounts from storage."""
    account = Account(name=name, user=owner)
    repo = AccountDBRepo(database=client.app["db"])

    with pytest.raises(AccountAlreadyExist):
        await repo.save(account)
