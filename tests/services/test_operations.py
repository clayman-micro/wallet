from datetime import datetime
from decimal import Decimal

import pytest

from wallet.domain.commands import AddOperationToAccount
from wallet.domain.entities import Account, Operation, OperationType
from wallet.services.operations import AddOperationToAccountHandler


@pytest.fixture(scope='function')
def account(fake, user):
    return Account(fake.credit_card_provider(), user=user, key=1)


async def test_add_operation_to_account(storage, account):
    now = datetime.now()

    cmd = AddOperationToAccount(Decimal('838'), account, created_on=now)
    handler = AddOperationToAccountHandler(storage)
    await handler.handle(cmd)

    assert storage.operations.entities[account.key] == [
        Operation(Decimal('838'), account, type=OperationType.expense, created_on=now)
    ]
    assert storage.was_committed
