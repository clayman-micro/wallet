import pytest
from _pytest.fixtures import FixtureRequest
from aiohttp import web
from passport.domain import User

from wallet.core.entities.accounts import Account, AccountFilters
from wallet.storage.accounts import AccountDBRepo


@pytest.fixture
def expected(request: FixtureRequest, owners: dict[int, User]) -> list[Account]:
    """Prepare expected result."""
    entities: list[Account] = []
    for item in request.param:
        owner = owners.get(item["owner"])
        account = Account(name=item["name"], user=owner)
        account.key = item.get("key", 0)

        entities.append(account)

    return entities


@pytest.mark.integration
async def test_success(client: web.Application, owner: User, accounts: list[Account], expected: list[Account]) -> None:
    """Successfully fetch accounts from storage."""
    repo = AccountDBRepo(database=client.app["db"])

    result = [account async for account in repo.fetch(filters=AccountFilters(user=owner))]

    assert result == expected
