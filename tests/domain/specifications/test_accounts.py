import asyncio
from unittest import mock

import pytest

from wallet.domain import EntityAlreadyExist
from wallet.domain.entities import Account
from wallet.domain.specifications import UniqueAccountNameSpecification
from wallet.domain.storage import AccountsRepo


async def test_account_name_available(account: Account) -> None:
    find = asyncio.Future()
    find.set_result([])

    repo = AccountsRepo()
    repo.find = mock.MagicMock(return_value=find)

    spec = UniqueAccountNameSpecification(repo)
    result = await spec.is_satisfied_by(account)

    assert result


async def test_account_name_should_be_unique(account: Account) -> None:
    account.key = 1

    find = asyncio.Future()
    find.set_result([account])

    repo = AccountsRepo()
    repo.find = mock.MagicMock(return_value=find)

    spec = UniqueAccountNameSpecification(repo)

    with pytest.raises(EntityAlreadyExist):
        acc = Account(account.name, account.user)
        await spec.is_satisfied_by(acc)

    repo.find.assert_called_once()
