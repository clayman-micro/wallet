import asyncio
from unittest import mock

import pytest  # type: ignore

from wallet.domain.entities import UserProvider


@pytest.fixture(scope="function")
def passport(user):
    identify = asyncio.Future()
    identify.set_result(user)

    provider = UserProvider()
    provider.identify = mock.MagicMock(return_value=identify)

    return provider
