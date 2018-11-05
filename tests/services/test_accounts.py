import pytest

from wallet.domain import EntityAlreadyExist
from wallet.domain.commands import RegisterAccount
from wallet.domain.entities import Account
from wallet.services.accounts import RegisterAccountHandler


async def test_register_account(fake, user, storage):
    name = fake.credit_card_provider()

    cmd = RegisterAccount(name, user=user)
    handler = RegisterAccountHandler(storage)
    await handler.handle(cmd)

    assert storage.accounts.entities[user.key] == [Account(name, user=user)]
    assert storage.was_committed


async def test_register_existed_account(fake, user, storage):
    name = fake.credit_card_provider()

    account = Account(name, user=user)
    await storage.accounts.add(account)

    with pytest.raises(EntityAlreadyExist):
        cmd = RegisterAccount(name, user=user)
        handler = RegisterAccountHandler(storage)
        await handler.handle(cmd)
