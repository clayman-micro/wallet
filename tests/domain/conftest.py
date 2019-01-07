from typing import Any

import pytest  # type: ignore

from wallet.domain.entities import Account, Tag, User


@pytest.fixture(scope="function")
def account(fake: Any, user: User) -> Account:
    return Account(1, fake.credit_card_provider(), user=user)


@pytest.fixture(scope="function")
def tag(fake: Any, user: User) -> Tag:
    return Tag(1, fake.safe_color_name(), user=user)
