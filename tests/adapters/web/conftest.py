import asyncio
from decimal import Decimal
from unittest import mock

import pytest  # type: ignore

from wallet.domain import Account, Balance, Operation, Tag, UserProvider


@pytest.fixture(scope="function")
def passport(user):
    identify = asyncio.Future()
    identify.set_result(user)

    provider = UserProvider()
    provider.identify = mock.MagicMock(return_value=identify)

    return provider


@pytest.fixture(scope="function")
def account(fake, user, month):
    return Account(key=0, name=fake.credit_card_provider(), user=user, balance=[
        Balance(month=month)
    ])


@pytest.fixture(scope="function")
def operation(fake, today, account):
    return Operation(
        key=0,
        amount=Decimal("838.00"),
        account=account,
        description="Fuel",
        created_on=today
    )


@pytest.fixture(scope="function")
def tag(fake, user):
    return Tag(key=0, name=fake.word(), user=user)
