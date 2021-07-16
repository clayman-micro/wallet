from logging import Logger
from typing import Callable

import pytest
from faker import Faker
from passport.domain import User

from wallet.core.entities import Account, AccountPayload
from wallet.core.services.accounts import AccountAlreadyExist, AccountService
from wallet.core.storage import Storage


StorageBuilder = Callable[[bool], Storage]


@pytest.fixture(scope="function")
def prepare_storage(fake_storage, fake_coroutine) -> StorageBuilder:
    def builder(exists: bool):
        fake_storage.accounts.exists = fake_coroutine(result=exists)
        fake_storage.accounts.save = fake_coroutine(result=1)

        return fake_storage

    return builder


@pytest.fixture(scope="function")
def payload(faker: Faker, user: User) -> AccountPayload:
    return AccountPayload(user, faker.credit_card_provider())


@pytest.mark.unit
async def test_success(logger: Logger, prepare_storage: StorageBuilder, payload: AccountPayload) -> None:
    service = AccountService(prepare_storage(exists=False), logger)
    account = await service.add(payload)

    expected = Account(name=payload.name, user=payload.user)
    expected.key = 1
    assert account == expected


@pytest.mark.unit
async def test_already_exists(logger: Logger, prepare_storage: StorageBuilder, payload: AccountPayload) -> None:
    storage = prepare_storage(exists=True)
    service = AccountService(storage, logger)

    with pytest.raises(AccountAlreadyExist):
        await service.add(payload)


@pytest.mark.unit
async def test_save_on_success(logger: Logger, prepare_storage: StorageBuilder, payload: AccountPayload) -> None:
    storage = prepare_storage(exists=False)
    service = AccountService(storage, logger)
    await service.add(payload)

    storage.accounts.save.assert_called_once()


@pytest.mark.unit
async def test_dont_save_on_dry_run(logger: Logger, prepare_storage: StorageBuilder, payload: AccountPayload) -> None:
    storage = prepare_storage(exists=False)
    service = AccountService(storage, logger)
    await service.add(payload, dry_run=True)

    storage.accounts.save.assert_not_called()
