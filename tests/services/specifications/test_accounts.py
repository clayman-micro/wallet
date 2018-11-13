import asyncio
from unittest import mock

import pytest  # type: ignore

from wallet.domain import EntityAlreadyExist
from wallet.domain.entities import Account
from wallet.domain.specifications import UniqueAccountNameSpecification


@pytest.mark.unit
async def test_account_name_available(accounts_repo, account: Account) -> None:
    find: asyncio.Future = asyncio.Future()
    find.set_result([])

    accounts_repo.find = mock.MagicMock(return_value=find)

    spec = UniqueAccountNameSpecification(accounts_repo)
    result = await spec.is_satisfied_by(account)

    assert result


@pytest.mark.unit
async def test_account_name_should_be_unique(accounts_repo, account: Account) -> None:
    find: asyncio.Future = asyncio.Future()
    find.set_result([account])

    accounts_repo.find = mock.MagicMock(return_value=find)

    spec = UniqueAccountNameSpecification(accounts_repo)

    with pytest.raises(EntityAlreadyExist):
        acc = Account(2, account.name, account.user)
        await spec.is_satisfied_by(acc)

    accounts_repo.find.assert_called_once()
