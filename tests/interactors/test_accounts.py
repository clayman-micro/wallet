import asyncio
from decimal import Decimal
from unittest import mock

import pytest

from wallet.entities import Account, Operation, OperationType
from wallet.interactors import accounts
from wallet.validation import ValidationError


@pytest.mark.interactors
@pytest.mark.parametrize('name, amount', (
    ('Foo', 100),
    ('Foo', 100.0),
    ('Foo', '100'),
    ('Foo', '100.0'),
))
async def test_create(owner, name, amount):
    save = asyncio.Future()
    save.set_result(1)

    repo = mock.MagicMock()
    repo.save = mock.MagicMock(return_value=save)

    interactor = accounts.CreateAccountInteractor(repo)
    interactor.set_params(owner, name, amount)
    account = await interactor.execute()

    repo.save.assert_called_once()
    assert isinstance(account, Account)
    assert account.pk == 1


@pytest.mark.interactors
@pytest.mark.parametrize('name, amount', (
    (None, None),
    ('', None),
    (None, ''),
    ('', ''),
    ('Foo', 'Bar')
))
async def test_create_failed(owner, name, amount):
    repo = mock.MagicMock()

    interactor = accounts.CreateAccountInteractor(repo)
    interactor.set_params(owner, name, amount)

    with pytest.raises(ValidationError):
        await interactor.execute()


@pytest.mark.interactors
async def test_get_accounts(owner):
    expected = [Account('Foo', Decimal(100.0), owner)]

    fetch = asyncio.Future()
    fetch.set_result(expected)

    repo = mock.MagicMock()
    repo.fetch = mock.MagicMock(return_value=fetch)

    interactor = accounts.GetAccountsInteractor(repo)
    interactor.set_params(owner)
    actual = await interactor.execute()

    repo.fetch.assert_called_with(owner=owner, name='')
    assert actual == expected


@pytest.mark.interactors
async def test_get_account(owner):
    expected = Account('Foo', Decimal(100.0), owner)

    fetch = asyncio.Future()
    fetch.set_result(expected)

    repo = mock.MagicMock()
    repo.fetch_account = mock.MagicMock(return_value=fetch)

    interactor = accounts.GetAccountInteractor(repo)
    interactor.set_params(owner, pk=1)
    actual = await interactor.execute()

    repo.fetch_account.assert_called_with(owner=owner, pk=1)
    assert actual == expected


@pytest.mark.interactors
async def test_update_name(owner):
    account = Account('Visa', Decimal(100.0), owner, pk=1)

    fetch = asyncio.Future()
    fetch.set_result(account)

    update = asyncio.Future()
    update.set_result(True)

    repo = mock.MagicMock()
    repo.fetch_account = mock.MagicMock(return_value=fetch)
    repo.update = mock.MagicMock(return_value=update)

    operations_repo = mock.MagicMock()
    operations_repo.fetch = mock.MagicMock()

    interactor = accounts.UpdateAccountInteractor(repo, operations_repo)
    interactor.set_params(owner, 1, name='Visa Classic')
    updated = await interactor.execute()

    repo.fetch_account.assert_called_with(owner, 1)
    repo.update.assert_called_with(account, ['name'])
    operations_repo.fetch.assert_not_called()

    assert updated.name == 'Visa Classic'
    assert updated.amount == account.amount


@pytest.mark.interactors
async def test_update_original_amount(owner):
    account = Account('Visa', Decimal(100.0), owner, pk=1)

    fetch = asyncio.Future()
    fetch.set_result(account)

    update = asyncio.Future()
    update.set_result(True)

    repo = mock.MagicMock()
    repo.fetch_account = mock.MagicMock(return_value=fetch)
    repo.update = mock.MagicMock(return_value=update)

    fetch_operations = asyncio.Future()
    fetch_operations.set_result([
        Operation(Decimal(100), account, type=OperationType.INCOME),
        Operation(Decimal(1100), account, type=OperationType.EXPENSE)
    ])

    operations_repo = mock.MagicMock()
    operations_repo.fetch = mock.MagicMock(return_value=fetch_operations)

    interactor = accounts.UpdateAccountInteractor(repo, operations_repo)
    interactor.set_params(owner, 1, original='2500')
    updated = await interactor.execute()

    repo.fetch_account.assert_called_with(owner, 1)
    repo.update.assert_called_with(account, ['original', 'amount'])
    operations_repo.fetch.assert_called_with(account)

    assert updated.amount == Decimal(-900.0)


@pytest.mark.interactors
@pytest.mark.parametrize('expected', (True, False))
async def test_remove_account(owner, expected):
    account = Account('Foo', Decimal(100.0), owner, pk=1)

    fetch = asyncio.Future()
    fetch.set_result(account)

    remove = asyncio.Future()
    remove.set_result(expected)

    repo = mock.MagicMock()
    repo.fetch_account = mock.MagicMock(return_value=fetch)
    repo.remove = mock.MagicMock(return_value=remove)

    interactor = accounts.RemoveAccountInteractor(repo)
    interactor.set_params(owner, account.pk)
    removed = await interactor.execute()

    repo.fetch_account.assert_called_with(owner, account.pk)
    repo.remove.assert_called_with(account)
    assert removed == expected
