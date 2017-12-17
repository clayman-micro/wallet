import asyncio
from datetime import datetime
from decimal import Decimal
from unittest import mock

import pytest

from wallet.entities import Account, Operation, OperationType, Owner
from wallet.interactors import operations


@pytest.fixture(scope='module')
def user():
    return Owner('test@clayman.pro', pk=1)


@pytest.fixture(scope='function')
def account(user):
    return Account('Visa', Decimal(0.0), user)


@pytest.fixture(scope='function')
def accounts_repo():
    async def create_repo():
        update = asyncio.Future()
        update.set_result(True)

        repo = mock.MagicMock()
        repo.update = mock.MagicMock(return_value=update)

        return repo
    return create_repo


@pytest.fixture(scope='function')
def operations_repo():
    async def create_repo(operation):
        save = asyncio.Future()
        save.set_result(1)

        fetch_by_pk = asyncio.Future()
        fetch_by_pk.set_result(operation)

        update = asyncio.Future()
        update.set_result(True)

        remove = asyncio.Future()
        remove.set_result(True)

        repo = mock.MagicMock()
        repo.save = mock.MagicMock(return_value=save)
        repo.fetch_by_pk = mock.MagicMock(return_value=fetch_by_pk)
        repo.update = mock.MagicMock(return_value=update)
        repo.remove = mock.MagicMock(return_value=remove)

        return repo
    return create_repo


@pytest.mark.clean
@pytest.mark.parametrize('amount, op_type, expected', (
    (100, OperationType.EXPENSE.value.lower(), Decimal(-100)),
    (100, OperationType.INCOME.value.lower(), Decimal(100)),
))
async def test_create(user, account, accounts_repo, operations_repo,
                      amount, op_type, expected):

    accounts = await accounts_repo()
    ops_repo = await operations_repo(None)

    interactor = operations.CreateOperationInteractor(accounts, ops_repo)
    interactor.set_params(amount, account, op_type)
    operation = await interactor.execute()

    ops_repo.save.assert_called_once()

    accounts.update.assert_called_with(account, amount=account.amount)

    assert isinstance(operation, Operation)
    assert operation.pk == 1
    assert operation.amount == Decimal(amount)
    assert operation.account == account
    assert operation.description == ''
    assert isinstance(operation.type, OperationType)
    assert operation.type.value.lower() == op_type

    assert account.amount == expected


@pytest.mark.clean
@pytest.mark.parametrize('amount, op_type, next_amount, expected', (
    (100, OperationType.EXPENSE, '200', Decimal(-200)),
    (100, OperationType.INCOME, '200', Decimal(200)),
))
async def test_update_amount(user, account, accounts_repo, operations_repo,
                             amount, op_type, next_amount, expected):

    accounts = await accounts_repo()

    operation = Operation(amount, account, type=op_type)
    ops_repo = await operations_repo(operation)

    account.apply_operation(operation)

    interactor = operations.UpdateOperationInteractor(accounts, ops_repo)
    interactor.set_params(account, 1, amount=next_amount)
    await interactor.execute()

    ops_repo.fetch_by_pk.assert_called_with(account, 1)
    ops_repo.update.assert_called_with(operation, amount=operation.amount)

    accounts.update.assert_called_with(account, amount=account.amount)

    assert account.amount == expected


@pytest.mark.clean
@pytest.mark.parametrize('amount, op_type, next_op_type, expected', (
    (100, OperationType.EXPENSE, OperationType.INCOME.value.lower(),
     Decimal(100)),
    (100, OperationType.INCOME, OperationType.EXPENSE.value.lower(),
     Decimal(-100)),
))
async def test_update_operation_type(user, account, accounts_repo,
                                     operations_repo, amount, op_type,
                                     next_op_type, expected):
    accounts = await accounts_repo()

    operation = Operation(amount, account, type=op_type)
    ops_repo = await operations_repo(operation)

    account.apply_operation(operation)

    interactor = operations.UpdateOperationInteractor(accounts, ops_repo)
    interactor.set_params(account, 1, type=next_op_type)
    await interactor.execute()

    ops_repo.fetch_by_pk.assert_called_with(account, 1)
    ops_repo.update.assert_called_with(operation, type=operation.type)

    accounts.update.assert_called_with(account, amount=account.amount)

    assert account.amount == expected


@pytest.mark.clean
@pytest.mark.parametrize('amount, op_type, payload', (
    (100, OperationType.EXPENSE, 'Foo'),
    (100, OperationType.INCOME, 'Foo'),
))
async def test_update_desc(user, account, accounts_repo, operations_repo,
                           amount, op_type, payload):

    accounts = await accounts_repo()

    operation = Operation(amount, account, type=op_type)
    ops_repo = await operations_repo(operation)

    interactor = operations.UpdateOperationInteractor(accounts, ops_repo)
    interactor.set_params(account, 1, description=payload)
    await interactor.execute()

    ops_repo.fetch_by_pk.assert_called_with(account, 1)
    ops_repo.update.assert_called_with(operation, description=payload)

    accounts.update.assert_not_called()


@pytest.mark.clean
@pytest.mark.parametrize('amount, op_type, payload', (
    (100, OperationType.EXPENSE, '2017-10-10T00:00:00'),
    (100, OperationType.INCOME, '2017-10-10T00:00:00'),
))
async def test_update_created(user, account, accounts_repo, operations_repo,
                              amount, op_type, payload):

    accounts = await accounts_repo()

    operation = Operation(amount, account, type=op_type)
    ops_repo = await operations_repo(operation)

    interactor = operations.UpdateOperationInteractor(accounts, ops_repo)
    interactor.set_params(account, 1, created_on=payload)
    await interactor.execute()

    created = datetime.strptime(payload, '%Y-%m-%dT%H:%M:%S')

    ops_repo.fetch_by_pk.assert_called_with(account, 1)
    ops_repo.update.assert_called_with(operation, created_on=created)

    accounts.update.assert_not_called()


@pytest.mark.clean
@pytest.mark.parametrize('amount, op_type, expected', (
    (100, OperationType.EXPENSE, Decimal(100)),
    (100, OperationType.INCOME, Decimal(-100)),
))
async def test_remove(user, account, accounts_repo, operations_repo, amount,
                      op_type, expected):

    accounts = await accounts_repo()

    operation = Operation(amount, account, type=op_type)
    ops_repo = await operations_repo(operation)

    interactor = operations.RemoveOperationInteractor(accounts, ops_repo)
    interactor.set_params(account, 1)
    await interactor.execute()

    ops_repo.fetch_by_pk.assert_called_with(account, 1)
    ops_repo.remove.assert_called_once()

    accounts.update.assert_called_with(account, amount=account.amount)

    assert account.amount == expected
