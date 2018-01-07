from datetime import datetime
from decimal import Decimal

import pytest

from wallet.entities import Account, Operation, OperationType, Tag


@pytest.mark.entities
def test_account(owner):
    now = datetime.now()

    account = Account.from_dict({
        'name': 'Foo',
        'amount': Decimal(1000.0),
        'owner': owner,
        'created_on': now
    })

    assert isinstance(account, Account)
    assert account.name == 'Foo'
    assert account.amount == Decimal(1000.0)
    assert account.original == Decimal(0.0)
    assert account.enabled is True
    assert account.created_on == now


@pytest.mark.entities
def test_operation(owner):
    now = datetime.now()

    account = Account('Foo', Decimal(1000.0), owner)

    operation = Operation.from_dict({
        'amount': Decimal(100.0),
        'description': 'Taxi',
        'account': account,
        'created_on': now
    })

    assert isinstance(operation, Operation)
    assert operation.description == 'Taxi'
    assert operation.amount == Decimal(100.0)
    assert operation.type == OperationType.EXPENSE
    assert operation.enabled is True
    assert operation.created_on == now
