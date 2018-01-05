import asyncio
from decimal import Decimal
from unittest import mock

import pytest

from wallet.adapters.accounts import AccountsAPIAdapter
from wallet.entities import Account, EntityAlreadyExist
from wallet.utils.accounts import AccountsFilter
from wallet.validation import ValidationError


@pytest.mark.adapters
async def test_fetch(loop, owner):
    expected = [Account('Foo', Decimal(100.0), owner, pk=1)]

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(expected)

    repo = mock.MagicMock()
    repo.fetch = mock.MagicMock(return_value=fetch)

    adapter = AccountsAPIAdapter(repo)
    result = await adapter.fetch(owner)

    assert result == {
        'accounts': [
            {'id': 1, 'name': 'Foo', 'amount': 100.0}
        ],
        'meta': {'total': 1}
    }


@pytest.mark.adapters
async def test_fetch_with_filters(loop, owner):
    expected = [Account('Foo', Decimal(100.0), owner, pk=1)]

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(expected)

    repo = mock.MagicMock()
    repo.fetch = mock.MagicMock(return_value=fetch)

    filters = AccountsFilter(name='Fo')

    adapter = AccountsAPIAdapter(repo)
    result = await adapter.fetch(owner, filters)

    assert result == {
        'accounts': [
            {'id': 1, 'name': 'Foo', 'amount': 100.0}
        ],
        'meta': {
            'total': 1,
            'filters': {
                'name': 'Fo'
            }
        }
    }


@pytest.mark.adapters
async def test_fetch_account(loop, owner):
    expected = Account('Foo', Decimal(100.0), owner, pk=1)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(expected)

    repo = mock.MagicMock()
    repo.fetch_account = mock.MagicMock(return_value=fetch)

    adapter = AccountsAPIAdapter(repo)
    result = await adapter.fetch_account(owner, pk=1)

    assert result == {
        'account': {'id': 1, 'name': 'Foo', 'amount': 100.0}
    }


@pytest.mark.adapters
async def test_add_account(loop, owner):
    save = asyncio.Future(loop=loop)
    save.set_result(1)

    repo = mock.MagicMock()
    repo.save = mock.MagicMock(return_value=save)

    adapter = AccountsAPIAdapter(repo)
    result = await adapter.add_account(owner, {'name': 'Foo', 'amount': '100.0'})

    assert result == {
        'account': {'id': 1, 'name': 'Foo', 'amount': 100.0}
    }


@pytest.mark.adapters
@pytest.mark.parametrize('payload', (
    {'name': ''},
    {'name': 'Foo', 'amount': ''},
    {'name': '', 'amount': 'foo'},
    {'name': 'Foo', 'amount': 'foo'},
))
async def test_add_account_failed(owner, payload):
    repo = mock.MagicMock()

    adapter = AccountsAPIAdapter(repo)
    with pytest.raises(ValidationError):
        await adapter.add_account(owner, payload)


@pytest.mark.adapters
async def test_add_already_existed_account(owner):
    repo = mock.MagicMock()
    repo.save = mock.MagicMock(side_effect=EntityAlreadyExist())

    adapter = AccountsAPIAdapter(repo)
    with pytest.raises(ValidationError):
        await adapter.add_account(owner, {'name': 'Foo', 'amount': '100.0'})


@pytest.mark.adapters
async def test_update_account_name(loop, owner):
    account = Account('Foo', Decimal(100.0), owner, pk=1)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(account)

    update = asyncio.Future(loop=loop)
    update.set_result(True)

    repo = mock.MagicMock()
    repo.fetch_account = mock.MagicMock(return_value=fetch)
    repo.update = mock.MagicMock(return_value=update)

    adapter = AccountsAPIAdapter(repo)
    result = await adapter.update_account(owner, 1, {'name': 'Bar'})

    assert result == {
        'account': {'id': 1, 'name': 'Bar', 'amount': Decimal(100.0)}
    }


@pytest.mark.adapters
async def test_update_account_original(loop, owner):
    account = Account('Foo', Decimal(100.0), owner, pk=1)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(account)

    update = asyncio.Future(loop=loop)
    update.set_result(True)

    repo = mock.MagicMock()
    repo.fetch_account = mock.MagicMock(return_value=fetch)
    repo.update = mock.MagicMock(return_value=update)

    fetch_operations = asyncio.Future(loop=loop)
    fetch_operations.set_result([])

    operations_repo = mock.MagicMock()
    operations_repo.fetch = mock.MagicMock(return_value=fetch_operations)

    adapter = AccountsAPIAdapter(repo, operations_repo)
    result = await adapter.update_account(owner, 1, {'original': '200'})

    assert result == {
        'account': {'id': 1, 'name': 'Foo', 'amount': Decimal(200.0)}
    }


@pytest.mark.adapters
async def test_update_account_amount(loop, owner):
    account = Account('Foo', Decimal(100.0), owner, pk=1)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(account)

    update = asyncio.Future(loop=loop)
    update.set_result(True)

    repo = mock.MagicMock()
    repo.fetch_account = mock.MagicMock(return_value=fetch)
    repo.update = mock.MagicMock(return_value=update)

    adapter = AccountsAPIAdapter(repo)
    result = await adapter.update_account(owner, 1, {'amount': '200'})

    assert result == {
        'account': {'id': 1, 'name': 'Foo', 'amount': Decimal(100.0)}
    }


@pytest.mark.adapters
async def test_remove_account(loop, owner):
    expected = Account('Foo', Decimal(100.0), owner, pk=1)

    remove = asyncio.Future(loop=loop)
    remove.set_result(1)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(expected)

    repo = mock.MagicMock()
    repo.fetch_account = mock.MagicMock(return_value=fetch)
    repo.remove = mock.MagicMock(return_value=remove)

    adapter = AccountsAPIAdapter(repo)
    await adapter.remove_account(owner, pk=1)
