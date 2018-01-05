import asyncio
from datetime import datetime
from decimal import Decimal
from unittest import mock

import pytest

from wallet.entities import EntityNotFound, Operation, OperationType
from wallet.interactors import operations
from wallet.utils.operations import OpsFilter
from wallet.validation import ValidationError


@pytest.fixture(scope='function')
def accounts_repo(loop):
    update = asyncio.Future(loop=loop)
    update.set_result(True)

    repo = mock.MagicMock()
    repo.update = mock.MagicMock(return_value=update)

    return repo


@pytest.mark.interactors
async def test_fetch(loop, owner, account):
    now = datetime.now()

    fetch = asyncio.Future(loop=loop)
    fetch.set_result([
        {'pk': 1}, {'pk': 2},
    ])

    repo = mock.MagicMock()
    repo.fetch = mock.MagicMock(return_value=fetch)

    interactor = operations.GetOperationsInteractor(repo)
    interactor.set_params(account)
    result = await interactor.execute()

    repo.fetch.assert_called_with(account=account, year=now.year,
                                  month=now.month)
    assert len(result) == 2


@pytest.mark.interactors
async def test_fetch_with_filters(loop, owner, account):
    filters = OpsFilter(year='2017', month='12')

    fetch = asyncio.Future(loop=loop)
    fetch.set_result([
        {'pk': 1}, {'pk': 2},
    ])

    repo = mock.MagicMock()
    repo.fetch = mock.MagicMock(return_value=fetch)

    interactor = operations.GetOperationsInteractor(repo)
    interactor.set_params(account, filters)
    result = await interactor.execute()

    repo.fetch.assert_called_with(account=account, year=2017, month=12)
    assert len(result) == 2


@pytest.mark.interactors
async def test_fetch_operation(loop, owner, account):
    operation = Operation(Decimal(100.0), account)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(operation)

    repo = mock.MagicMock()
    repo.fetch_operation = mock.MagicMock(return_value=fetch)

    interactor = operations.GetOperationInteractor(repo)
    interactor.set_params(account, 1)
    result = await interactor.execute()

    repo.fetch_operation.assert_called_with(account, 1)
    assert result == operation


@pytest.mark.interactors
async def test_fetch_operation_failed(loop, owner, account):
    repo = mock.MagicMock()
    repo.fetch_operation = mock.MagicMock(side_effect=EntityNotFound)

    interactor = operations.GetOperationInteractor(repo)
    interactor.set_params(account, 1)

    with pytest.raises(EntityNotFound):
        await interactor.execute()

    repo.fetch_operation.assert_called_with(account, 1)


@pytest.mark.interactors
@pytest.mark.parametrize('payload, expected', (
    ({'amount': 100, 'type': OperationType.EXPENSE.value.lower()},
     Decimal(-100)),
    ({'amount': 100, 'type': OperationType.INCOME.value.lower()},
     Decimal(100)),
    ({'amount': 100, 'type': OperationType.EXPENSE.value.lower(),
      'created_on': '2018-01-05T00:00:00'}, Decimal(-100)),
))
async def test_create(loop, owner, account, accounts_repo, payload, expected):
    save = asyncio.Future(loop=loop)
    save.set_result(1)

    repo = mock.MagicMock()
    repo.save = mock.MagicMock(return_value=save)

    interactor = operations.CreateOperationInteractor(accounts_repo, repo)
    interactor.set_params(account, payload)
    operation = await interactor.execute()

    accounts_repo.update.assert_called_with(account, ['amount'])
    repo.save.assert_called_once()

    assert isinstance(operation, Operation)
    assert operation.pk == 1

    assert account.amount == expected


@pytest.mark.interactors
@pytest.mark.parametrize('payload', (
    {},
    {'amount': 'foo'},
    {'amount': 'foo', 'type': 'transfer'},
    {'amount': '100', 'type': OperationType.EXPENSE.value.lower(),
     'created_on': 'foo'},
    {'amount': '100', 'type': OperationType.EXPENSE.value.lower(),
     'created_on': '2018-01-05'},
))
async def test_create_failed(owner, account, accounts_repo, payload):
    repo = mock.MagicMock()
    repo.save = mock.MagicMock()

    interactor = operations.CreateOperationInteractor(accounts_repo, repo)
    interactor.set_params(account, payload)

    with pytest.raises(ValidationError):
        await interactor.execute()

    accounts_repo.update.assert_not_called()
    repo.save.assert_not_called()


@pytest.mark.interactors
@pytest.mark.parametrize('op, payload, expected', (
    ((Decimal(100.00), OperationType.EXPENSE), {'amount': '200'},
     Decimal(-200)),
    ((Decimal(100.00), OperationType.INCOME), {'amount': '200'},
     Decimal(200)),
    ((Decimal(100.00), OperationType.EXPENSE),
     {'type': OperationType.INCOME.value.lower()}, Decimal(100)),
    ((Decimal(100.00), OperationType.INCOME),
     {'type': OperationType.EXPENSE.value.lower()}, Decimal(-100)),
))
async def test_update_with_change_amount(loop, owner, account, accounts_repo,
                                         op, payload, expected):
    operation = Operation(op[0], account, type=op[1])
    account.apply_operation(operation)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(operation)

    update = asyncio.Future(loop=loop)
    update.set_result(True)

    repo = mock.MagicMock()
    repo.fetch_operation = mock.MagicMock(return_value=fetch)
    repo.update = mock.MagicMock(return_value=update)

    interactor = operations.UpdateOperationInteractor(accounts_repo, repo)
    interactor.set_params(account, 1, payload)
    result = await interactor.execute()

    assert isinstance(result, Operation)

    repo.fetch_operation.assert_called_with(account, 1)
    repo.update.assert_called_with(operation, list(payload.keys()))

    accounts_repo.update.assert_called_with(account, ['amount'])

    assert account.amount == expected


@pytest.mark.interactors
@pytest.mark.parametrize('op, payload', (
    ((Decimal(100.00), OperationType.EXPENSE), {'description': 'Meal'}),
    ((Decimal(100.00), OperationType.INCOME), {'description': 'Meal'}),
    ((Decimal(100.00), OperationType.EXPENSE),
     {'created_on': '2018-01-01T00:00:00'}),
    ((Decimal(100.00), OperationType.INCOME),
     {'created_on': '2018-01-01T00:00:00'}),
))
async def test_update_without_change_amount(loop, owner, account, accounts_repo,
                                            op, payload):
    operation = Operation(op[0], account, type=op[1])
    account.apply_operation(operation)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(operation)

    update = asyncio.Future(loop=loop)
    update.set_result(True)

    repo = mock.MagicMock()
    repo.fetch_operation = mock.MagicMock(return_value=fetch)
    repo.update = mock.MagicMock(return_value=update)

    interactor = operations.UpdateOperationInteractor(accounts_repo, repo)
    interactor.set_params(account, 1, payload)
    result = await interactor.execute()

    assert isinstance(result, Operation)

    repo.fetch_operation.assert_called_with(account, 1)
    repo.update.assert_called_with(operation, list(payload.keys()))

    accounts_repo.update.assert_not_called()


@pytest.mark.interactors
@pytest.mark.parametrize('amount, op_type, expected', (
    (100, OperationType.EXPENSE, Decimal(100)),
    (100, OperationType.INCOME, Decimal(-100)),
))
async def test_remove(loop, owner, account, accounts_repo, amount, op_type,
                      expected):

    operation = Operation(amount, account, type=op_type)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(operation)

    remove = asyncio.Future(loop=loop)
    remove.set_result(True)

    repo = mock.MagicMock()
    repo.fetch_operation = mock.MagicMock(return_value=fetch)
    repo.remove = mock.MagicMock(return_value=remove)

    interactor = operations.RemoveOperationInteractor(accounts_repo, repo)
    interactor.set_params(account, 1)
    await interactor.execute()

    repo.fetch_operation.assert_called_with(account, 1)
    repo.remove.assert_called_once()

    accounts_repo.update.assert_called_with(account, ('amount', ))

    assert account.amount == expected
