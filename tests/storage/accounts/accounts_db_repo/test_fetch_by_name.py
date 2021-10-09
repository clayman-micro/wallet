import pytest
from _pytest.fixtures import FixtureRequest
from aiohttp import web
from passport.domain import User

from wallet.core.entities.accounts import Account
from wallet.core.exceptions import AccountNotFound
from wallet.storage.accounts import AccountDBRepo


@pytest.fixture
def expected(request: FixtureRequest, owners: dict[int, User]) -> Account:
    """Prepare expected result."""
    owner = owners.get(request.param["owner"])
    account = Account(name=request.param["name"], user=owner)
    account.key = request.param.get("key", 0)

    return account


@pytest.mark.integration
async def test_success(
    client: web.Application, owner: User, name: str, accounts: list[Account], expected: Account
) -> None:
    """Successfully fetch account from storage by key."""
    repo = AccountDBRepo(database=client.app["db"])

    result = await repo.fetch_by_name(user=owner, name=name)

    assert result == expected


@pytest.mark.integration
async def test_missing(client: web.Application, owner: User, name: str, accounts: list[Account]) -> None:
    """Fetch missing account from storage by key."""
    repo = AccountDBRepo(database=client.app["db"])

    with pytest.raises(AccountNotFound):
        await repo.fetch_by_name(user=owner, name=name)
