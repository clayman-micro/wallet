import asyncio
from unittest import mock

import pytest  # type: ignore

from wallet.domain import Account
from wallet.domain.storage import EntityAlreadyExist
from wallet.services.accounts import AccountsService


class TestAccountsService:
    @pytest.mark.unit
    async def test_register_account(self, fake, user, storage):
        name = fake.credit_card_provider()

        add = asyncio.Future()
        add.set_result(1)

        find = asyncio.Future()
        find.set_result([])

        storage.accounts.add = mock.MagicMock(return_value=add)
        storage.accounts.find_by_name = mock.MagicMock(return_value=find)

        account = Account(key=0, name=name, user=user)

        service = AccountsService(storage)
        await service.register(account)

        storage.accounts.add.assert_called_once()
        assert account == Account(key=1, name=name, user=user)
        assert storage.was_committed

    @pytest.mark.unit
    async def test_reject_account_with_duplicate_name(
        self, fake, user, storage
    ):
        name = fake.credit_card_provider()

        find = asyncio.Future()
        find.set_result([Account(key=1, name=name, user=user)])

        storage.accounts.find_by_name = mock.MagicMock(return_value=find)

        account = Account(key=0, name=name, user=user)

        with pytest.raises(EntityAlreadyExist):
            service = AccountsService(storage)
            await service.register(account)

        storage.accounts.find_by_name.assert_called()
