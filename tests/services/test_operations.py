import asyncio
from datetime import datetime
from decimal import Decimal
from unittest import mock

import pytest  # type: ignore

from wallet.domain.entities import Account, Operation, OperationType
from wallet.services.operations import OperationsService


@pytest.fixture(scope='function')
def account(fake, user) -> Account:
    return Account(1, fake.credit_card_provider(), user=user)


class TestOperationsService:

    @pytest.mark.unit
    async def test_add_operation_to_account(self, account, storage):
        now = datetime.now()

        update_account = asyncio.Future()
        update_account.set_result(True)

        storage.accounts.update = mock.MagicMock(return_value=update_account)

        add = asyncio.Future()
        add.set_result(1)

        storage.operations.add = mock.MagicMock(return_value=add)

        service = OperationsService(storage)
        operation = await service.add_to_account(account, Decimal('838'),
                                                 created_on=now)

        assert operation == Operation(1, Decimal('838'), account,
                                      type=OperationType.expense,
                                      created_on=now)

        storage.operations.add.assert_called()
        storage.accounts.update.assert_called()
        assert storage.was_committed
