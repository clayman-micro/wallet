import asyncio
from unittest import mock

import pytest

from wallet.adapters.tags import TagsAPIAdapter
from wallet.entities import Tag
from wallet.utils.tags import TagsFilter


@pytest.mark.adapters
@pytest.mark.parametrize('filters, meta', (
    (None, {'total': 2}),
    (TagsFilter(''), {'total': 2}),
    (TagsFilter('Foo'), {'total': 2, 'filters': {'name': 'Foo'}})
))
async def test_fetch_tags(loop, owner, filters, meta):
    fetch = asyncio.Future(loop=loop)
    fetch.set_result([Tag('Foo', owner, pk=1), Tag('Bar', owner, pk=2)])

    repo = mock.MagicMock()
    repo.fetch = mock.MagicMock(return_value=fetch)

    adapter = TagsAPIAdapter(repo)
    result = await adapter.fetch(owner, filters=filters)

    assert result == {
        'tags': [{'id': 1, 'name': 'Foo'}, {'id': 2, 'name': 'Bar'}],
        'meta': meta
    }


@pytest.mark.adapters
async def test_add_tag(loop, owner):
    save = asyncio.Future(loop=loop)
    save.set_result(2)

    repo = mock.MagicMock()
    repo.save_tag = mock.MagicMock(return_value=save)

    adapter = TagsAPIAdapter(repo)
    result = await adapter.add_tag(owner, {'name': 'Foo'})

    assert result == {'tag': {'id': 2, 'name': 'Foo'}}


@pytest.mark.adapters
async def test_fetch_tag(loop, owner):
    fetch = asyncio.Future(loop=loop)
    fetch.set_result(Tag('Foo', owner, pk=2))

    repo = mock.MagicMock()
    repo.fetch_tag = mock.MagicMock(return_value=fetch)

    adapter = TagsAPIAdapter(repo)
    result = await adapter.fetch_tag(owner, 2)

    assert result == {'tag': {'id': 2, 'name': 'Foo'}}


@pytest.mark.adapters
async def test_update_tag(loop, owner):
    fetch = asyncio.Future(loop=loop)
    fetch.set_result(Tag('Foo', owner, pk=2))

    update = asyncio.Future(loop=loop)
    update.set_result(True)

    repo = mock.MagicMock()
    repo.fetch_tag = mock.MagicMock(return_value=fetch)
    repo.update_tag = mock.MagicMock(return_value=update)

    adapter = TagsAPIAdapter(repo)
    result = await adapter.update_tag(owner, 2, {'name': 'Bar'})

    assert result == {'tag': {'id': 2, 'name': 'Bar'}}


@pytest.mark.adapters
async def test_remove_tag(loop, owner):
    fetch = asyncio.Future(loop=loop)
    fetch.set_result(Tag('Foo', owner, pk=2))

    remove = asyncio.Future(loop=loop)
    remove.set_result(True)

    repo = mock.MagicMock()
    repo.fetch_tag = mock.MagicMock(return_value=fetch)
    repo.remove_tag = mock.MagicMock(return_value=remove)

    adapter = TagsAPIAdapter(repo)
    await adapter.remove_tag(owner, 2)
