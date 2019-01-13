from decimal import Decimal

import pytest  # type: ignore

from wallet.domain import Account, Balance, Operation, Tag


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
