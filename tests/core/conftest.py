import asyncio
from logging import Logger

import pytest

from wallet.core.entities import Account, Category
from wallet.core.storage import Storage


@pytest.fixture(scope="function")
def logger(mocker) -> Logger:
    fake_logger = mocker.MagicMock()

    fake_logger.debug = mocker.MagicMock()
    fake_logger.info = mocker.MagicMock()
    fake_logger.error = mocker.MagicMock()

    return fake_logger


@pytest.fixture(scope="function")
def fake_storage(mocker) -> Storage:
    storage = mocker.MagicMock()

    storage.accounts = mocker.MagicMock()
    storage.categories = mocker.MagicMock()
    storage.operations = mocker.MagicMock()

    return storage


@pytest.fixture(scope="function")
def fake_coroutine(mocker):
    def coro(result):
        future = asyncio.Future()
        future.set_result(result)

        return mocker.MagicMock(return_value=future)

    return coro


@pytest.fixture(scope="function")
def account(faker, user) -> Account:
    account = Account(name=faker.credit_card_provider(), user=user)
    account.key = 1

    return account


@pytest.fixture(scope="function")
def category(faker, user) -> Category:
    category = Category(name=faker.job(), user=user)
    category.key = 1

    return category
