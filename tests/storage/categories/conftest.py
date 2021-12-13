import pytest

from wallet.storage.categories import CategoryDBRepo


@pytest.fixture
def repo(client) -> CategoryDBRepo:
    return CategoryDBRepo(database=client.app["db"])
