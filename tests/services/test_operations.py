import asyncio
from datetime import datetime
from decimal import Decimal
from unittest import mock

import pytest  # type: ignore

from wallet.domain.commands import AddOperationToAccount
from wallet.domain.entities import Account, OperationType
from wallet.services.operations import AddOperationToAccountHandler


@pytest.fixture(scope='function')
def account(fake, user) -> Account:
    return Account(1, fake.credit_card_provider(), user=user)


@pytest.mark.unit
async def test_add_operation_to_account(storage, account):
    now = datetime.now()

    update_account = asyncio.Future()
    update_account.set_result(True)

    storage._accounts.update = mock.MagicMock(return_value=update_account)

    cmd = AddOperationToAccount(Decimal('838'), account, created_on=now)
    handler = AddOperationToAccountHandler(storage)
    await handler.handle(cmd)

    assert len(storage.operations.entities[account.key]) == 1

    operation = storage.operations.entities[account.key][0]
    assert operation.amount == Decimal('838')
    assert operation.account == account
    assert operation.type == OperationType.expense

    assert account.balance[0].expenses == Decimal('838')
    assert account.balance[0].rest == Decimal('-838')

    storage._accounts.update.assert_called()

    assert storage.was_committed
