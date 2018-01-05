import asyncio
from datetime import datetime
from decimal import Decimal
from unittest import mock

import pytest

from wallet.adapters.operations import OperationsAPIAdapter
from wallet.entities import EntityNotFound, Operation, OperationType
from wallet.utils.operations import OpsFilter


@pytest.fixture(scope='function')
def accounts_repo(loop, account):
    fetch = asyncio.Future(loop=loop)
    fetch.set_result(account)

    update = asyncio.Future(loop=loop)
    update.set_result(1)

    repo = mock.MagicMock()
    repo.fetch_account = mock.MagicMock(return_value=fetch)
    repo.update = mock.MagicMock(return_value=update)

    return repo


@pytest.mark.adapters
async def test_fetch_account(owner, account, accounts_repo):
    adapter = OperationsAPIAdapter(accounts_repo, None)
    result = await adapter.fetch_account(owner, account.pk)

    assert result == account


@pytest.mark.adapters
async def test_fetch_account_failed(owner, account):
    repo = mock.MagicMock()
    repo.fetch_account = mock.MagicMock(side_effect=EntityNotFound)

    adapter = OperationsAPIAdapter(repo, None)
    with pytest.raises(EntityNotFound):
        await adapter.fetch_account(owner, account.pk)


@pytest.mark.adapters
@pytest.mark.parametrize('filters,meta', (
    (None, {'total': 1}),
    (OpsFilter.from_dict({'year': '2017', 'month': '09'}), {
        'total': 1, 'filters': {'year': '2017', 'month': '09'}
    }),
))
async def test_fetch_operations(owner, account, accounts_repo, filters, meta):
    now = datetime.now()

    fetch = asyncio.Future()
    fetch.set_result([
        Operation(Decimal(100.0), account, pk=1, description='Food',
                  created_on=now)
    ])

    repo = mock.MagicMock()
    repo.fetch = mock.MagicMock(return_value=fetch)

    adapter = OperationsAPIAdapter(accounts_repo, repo)
    result = await adapter.fetch(owner, account.pk, filters=filters)

    repo.fetch.assert_called_once()
    assert result == {
        'operations': [{
            'id': 1, 'type': 'expense', 'amount': Decimal(100.0), 'description': 'Food',
            'created_on': now.strftime('%Y-%m-%dT%H:%M:%S')
        }],
        'meta': meta
    }


@pytest.mark.adapters
async def test_add_operation(owner, account, accounts_repo):
    now = datetime.now()

    save = asyncio.Future()
    save.set_result(2)

    repo = mock.MagicMock()
    repo.save = mock.MagicMock(return_value=save)

    payload = {
        'amount': Decimal(143.50),
        'type': OperationType.EXPENSE.value.lower(),
        'description': 'Taxi',
        'created_on': now.strftime('%Y-%m-%dT%H:%M:%S')
    }

    adapter = OperationsAPIAdapter(accounts_repo, repo)
    result = await adapter.add_operation(owner, account.pk, payload)

    repo.save.assert_called_once()
    assert result == {
        'operation': {
            'id': 2,
            'type': 'expense',
            'amount': Decimal(143.50),
            'description': 'Taxi',
            'created_on': now.strftime('%Y-%m-%dT%H:%M:%S')
        }
    }


@pytest.mark.adapters
async def test_fetch_operation(owner, account, accounts_repo):
    now = datetime.now()

    fetch = asyncio.Future()
    fetch.set_result(Operation(Decimal(100.0), account, pk=1,
                     description='Food', created_on=now))

    repo = mock.MagicMock()
    repo.fetch_operation = mock.MagicMock(return_value=fetch)

    adapter = OperationsAPIAdapter(accounts_repo, repo)
    result = await adapter.fetch_operation(owner, account.pk, operation_pk=1)

    assert result == {
        'operation': {
            'id': 1,
            'type': 'expense',
            'amount': Decimal(100.0),
            'description': 'Food',
            'created_on': now.strftime('%Y-%m-%dT%H:%M:%S')
        }
    }


@pytest.mark.adapters
async def test_fetch_missing_operation(owner, account, accounts_repo):
    repo = mock.MagicMock()
    repo.fetch_operation = mock.MagicMock(side_effect=EntityNotFound)

    with pytest.raises(EntityNotFound):
        adapter = OperationsAPIAdapter(accounts_repo, repo)
        await adapter.fetch_operation(owner, account.pk, operation_pk=1)


@pytest.mark.adapters
async def test_update_operation(owner, account, accounts_repo):
    now = datetime.now()

    fetch = asyncio.Future()
    fetch.set_result(
        Operation(Decimal(100.0), account, pk=1, description='Food',
                  created_on=now)
    )

    update = asyncio.Future()
    update.set_result(1)

    repo = mock.MagicMock()
    repo.fetch_operation = mock.MagicMock(return_value=fetch)
    repo.update = mock.MagicMock(return_value=update)

    payload = {'type': 'income'}

    adapter = OperationsAPIAdapter(accounts_repo, repo)
    result = await adapter.update_operation(owner, account.pk, 1, payload)

    assert result == {
        'operation': {
            'id': 1,
            'type': 'income',
            'amount': Decimal(100.0),
            'description': 'Food',
            'created_on': now.strftime('%Y-%m-%dT%H:%M:%S')
        }
    }


@pytest.mark.adapters
async def test_remove_operation(owner, account, accounts_repo):
    now = datetime.now()

    fetch = asyncio.Future()
    fetch.set_result(
        Operation(Decimal(100.0), account, pk=1, description='Food',
                  created_on=now)
    )

    remove = asyncio.Future()
    remove.set_result(1)

    repo = mock.MagicMock()
    repo.fetch_operation = mock.MagicMock(return_value=fetch)
    repo.remove = mock.MagicMock(return_value=remove)

    adapter = OperationsAPIAdapter(accounts_repo, repo)
    await adapter.remove_operation(owner, account.pk, 1)


@pytest.mark.adapters
async def test_remove_missing_operation(owner, account, accounts_repo):
    remove = asyncio.Future()
    remove.set_result(1)

    repo = mock.MagicMock()
    repo.fetch_operation = mock.MagicMock(side_effect=EntityNotFound)
    repo.remove = mock.MagicMock(return_value=remove)

    with pytest.raises(EntityNotFound):
        adapter = OperationsAPIAdapter(accounts_repo, repo)
        await adapter.remove_operation(owner, account.pk, 1)
