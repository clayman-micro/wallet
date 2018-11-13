import pytest  # type: ignore

from wallet.domain import EntityAlreadyExist
from wallet.domain.commands import RegisterAccount
from wallet.domain.entities import Account
from wallet.services.accounts import RegisterAccountHandler


@pytest.mark.unit
async def test_register_account(fake, user, storage):
    name = fake.credit_card_provider()

    cmd = RegisterAccount(name, user=user)
    handler = RegisterAccountHandler(storage)
    await handler.handle(cmd)

    assert storage.accounts.entities[user.key] == [Account(0, name, user)]
    assert storage.was_committed


@pytest.mark.unit
async def test_register_existed_account(fake, user, storage):
    name = fake.credit_card_provider()

    account = Account(1, name, user)
    await storage.accounts.add(account)

    with pytest.raises(EntityAlreadyExist):
        cmd = RegisterAccount(name, user=user)
        handler = RegisterAccountHandler(storage)
        await handler.handle(cmd)


# async def remove_account(fake, user, storage):
#     name = fake.credit_card_provider()
#
#     account = Account(name, user=user, key=1)
#     storage.accounts.entities[user.key].append(account)
#
#     cmd = RemoveAccount(account)
#     handler = RemoveAccountHandler(storage)
#     await handler.handle(cmd)
