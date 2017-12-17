import asyncio
from decimal import Decimal
from unittest import mock

import pytest

from wallet.entities import Account, Operation, OperationType, Owner
from wallet.interactors import accounts
from wallet.validation import ValidationError


@pytest.fixture(scope='module')
def user():
    return Owner('test@clayman.pro', pk=1)


@pytest.fixture(scope='function')
def accounts_repo():
    async def create_repo(fetch_result=None, remove_result=None,
                          exists_result=None):
        check_exists = asyncio.Future()
        check_exists.set_result(exists_result)

        fetch = asyncio.Future()
        fetch.set_result(fetch_result)

        save = asyncio.Future()
        save.set_result(1)

        update = asyncio.Future()
        update.set_result(True)

        remove = asyncio.Future()
        remove.set_result(remove_result)

        repo = mock.MagicMock()
        repo.check_exists = mock.MagicMock(return_value=check_exists)
        repo.fetch = mock.MagicMock(return_value=fetch)
        repo.fetch_by_pk = mock.MagicMock(return_value=fetch)
        repo.save = mock.MagicMock(return_value=save)
        repo.update = mock.MagicMock(return_value=update)
        repo.remove = mock.MagicMock(return_value=remove)

        return repo
    return create_repo


@pytest.mark.clean
@pytest.mark.parametrize('name, amount', (
    ('Foo', 100),
    ('Foo', 100.0),
    ('Foo', '100'),
    ('Foo', '100.0'),
))
async def test_create(user, accounts_repo, name, amount):
    repo = await accounts_repo()

    interactor = accounts.CreateAccountInteractor(repo)
    interactor.set_params(user, name, amount)

    account = await interactor.execute()

    repo.check_exists.assert_called_with(user, name)
    repo.save.assert_called_once()

    assert isinstance(account, Account)
    assert account.pk == 1
    assert account.name == 'Foo'
    assert account.amount == Decimal(100.0)
    assert account.original == Decimal(100.0)


@pytest.mark.clean
@pytest.mark.parametrize('name, amount', (
    (None, None),
    ('', None),
    (None, ''),
    ('', ''),
    ('Foo', 'Bar')
))
async def test_create_failed(user, accounts_repo, name, amount):
    repo = await accounts_repo()

    interactor = accounts.CreateAccountInteractor(repo)
    interactor.set_params(user, name, amount)

    with pytest.raises(ValidationError):
        await interactor.execute()


@pytest.mark.clean
async def test_create_with_already_existed_account(user, accounts_repo):
    repo = await accounts_repo(exists_result=True)

    interactor = accounts.CreateAccountInteractor(repo)
    interactor.set_params(user, 'Foo', 0.0)

    with pytest.raises(ValidationError):
        await interactor.execute()


@pytest.mark.clean
async def test_get_accounts(user, accounts_repo):
    expected = [Account('Foo', Decimal(100.0), user)]

    repo = await accounts_repo(fetch_result=expected)

    interactor = accounts.GetAccountsInteractor(repo)
    interactor.set_params(user)

    actual = await interactor.execute()

    repo.fetch.assert_called_with(owner=user, name='')
    assert actual == expected


@pytest.mark.clean
async def test_get_account(user, accounts_repo):
    expected = Account('Foo', Decimal(100.0), user)

    repo = await accounts_repo(fetch_result=expected)

    interactor = accounts.GetAccountInteractor(repo)
    interactor.set_params(user, pk=1)

    actual = await interactor.execute()

    repo.fetch_by_pk.assert_called_with(owner=user, pk=1)
    assert actual == expected


@pytest.mark.clean
async def test_update_name(user, accounts_repo):
    account = Account('Visa', Decimal(100.0), user, pk=1)

    repo = await accounts_repo(fetch_result=account)

    operations_repo = mock.MagicMock()
    operations_repo.fetch = mock.MagicMock()

    interactor = accounts.UpdateAccountInteractor(repo, operations_repo)
    interactor.set_params(user, 1, name='Visa Classic')
    acc = await interactor.execute()

    operations_repo.fetch.assert_not_called()

    repo.fetch_by_pk.assert_called_with(user, 1)
    repo.update.assert_called_with(account, name='Visa Classic')

    assert acc.name == 'Visa Classic'
    assert acc.amount == account.amount


@pytest.mark.clean
async def test_update_original_amount(user, accounts_repo):
    account = Account('Visa', Decimal(100.0), user, pk=1)

    fetch = asyncio.Future()
    fetch.set_result([
        Operation(Decimal(100), account, type=OperationType.INCOME),
        Operation(Decimal(1100), account, type=OperationType.EXPENSE)
    ])

    operations_repo = mock.MagicMock()
    operations_repo.fetch = mock.MagicMock(return_value=fetch)

    repo = await accounts_repo(fetch_result=account)

    interactor = accounts.UpdateAccountInteractor(repo, operations_repo)
    interactor.set_params(user, 1, original='2500')
    acc = await interactor.execute()

    operations_repo.fetch.assert_called_with(account)

    repo.fetch_by_pk.assert_called_with(user, 1)
    repo.update.assert_called_with(account, amount=Decimal(-900.0),
                                   original=Decimal(2500.0))

    assert acc.amount == Decimal(-900.0)


@pytest.mark.clean
@pytest.mark.parametrize('expected', (True, False))
async def test_remove_account(user, accounts_repo, expected):
    account = Account('Foo', Decimal(100.0), user, pk=1)

    repo = await accounts_repo(fetch_result=account, remove_result=expected)

    interactor = accounts.RemoveAccountInteractor(repo)
    interactor.set_params(user, account.pk)
    removed = await interactor.execute()

    repo.fetch_by_pk.assert_called_with(user, account.pk)
    repo.remove.assert_called_with(account)
    assert removed == expected
