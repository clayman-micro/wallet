from typing import Any

import pytest

from wallet.domain.entities import Account, Tag, User


@pytest.fixture(scope='function')
def account(fake: Any, user: User) -> Account:
    return Account(fake.credit_card_provider(), user=user)


@pytest.fixture(scope='function')
def tag(fake: Any, user: User) -> Tag:
    return Tag(fake.safe_color_name(), user=user)
