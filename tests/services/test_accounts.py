import asyncio
from unittest import mock

import pytest  # type: ignore

from wallet.domain import EntityAlreadyExist
from wallet.domain.entities import Account
from wallet.services.accounts import AccountsService


class TestAccountsService:

    @pytest.mark.unit
    async def test_register_account(self, fake, user, storage):
        name = fake.credit_card_provider()

        add = asyncio.Future()
        add.set_result(1)

        storage.accounts.add = mock.MagicMock(return_value=add)

        service = AccountsService(storage)
        account = await service.register(name=name, user=user)

        storage.accounts.add.assert_called_once()
        assert account == Account(key=1, name=name, user=user)
        assert storage.was_committed

    @pytest.mark.unit
    async def test_reject_account_with_duplicate_name(self, fake, user, storage):
        name = fake.credit_card_provider()

        find = asyncio.Future()
        find.set_result([Account(key=1, name=name, user=user)])

        storage.accounts.find = mock.MagicMock(return_value=find)

        with pytest.raises(EntityAlreadyExist):
            service = AccountsService(storage)
            await service.register(name, user)

        storage.accounts.find.assert_called()
