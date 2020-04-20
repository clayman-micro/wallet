from typing import Any

import pytest  # type: ignore
from passport.domain import User

from wallet.domain import Account


@pytest.fixture(scope="function")
def account(fake: Any, user: User) -> Account:
    return Account(1, fake.credit_card_provider(), user=user)
