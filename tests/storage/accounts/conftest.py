import pytest

from wallet.storage.accounts import AccountDBRepo


@pytest.fixture
def repo(client) -> AccountDBRepo:
    return AccountDBRepo(database=client.app["db"])
