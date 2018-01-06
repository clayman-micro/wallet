import asyncio
from unittest import mock

import pytest

from wallet.entities import EntityAlreadyExist, Tag
from wallet.interactors import tags
from wallet.validation import ValidationError


@pytest.mark.interactors
async def test_add(loop, owner):
    save = asyncio.Future(loop=loop)
    save.set_result(1)

    repo = mock.MagicMock()
    repo.save_tag = mock.MagicMock(return_value=save)

    interactor = tags.AddTagInteractor(repo)
    interactor.set_params(owner, 'Foo')
    tag = await interactor.execute()

    repo.save_tag.assert_called_once()
    assert isinstance(tag, Tag)
    assert tag.pk == 1
    assert tag.name == 'Foo'


@pytest.mark.interactors
@pytest.mark.parametrize('name', (None, ''))
async def test_add_failed(owner, name):
    repo = mock.MagicMock()

    interactor = tags.AddTagInteractor(repo)
    interactor.set_params(owner, name)

    with pytest.raises(ValidationError):
        await interactor.execute()


@pytest.mark.interactors
@pytest.mark.parametrize('name', ('', 'Foo'))
async def test_fetch_tags(loop, owner, name):
    expected = [Tag('Foo', owner), Tag('Bar', owner)]

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(expected)

    repo = mock.MagicMock()
    repo.fetch = mock.MagicMock(return_value=fetch)

    interactor = tags.FetchTagsInteractor(repo)
    interactor.set_params(owner, name)
    result = await interactor.execute()

    repo.fetch.assert_called_with(owner=owner, name=name)
    assert result == expected


@pytest.mark.interactors
async def test_fetch_tag(loop, owner):
    expected = Tag('Foo', owner)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(expected)

    repo = mock.MagicMock()
    repo.fetch_tag = mock.MagicMock(return_value=fetch)

    interactor = tags.FetchTagInteractor(repo)
    interactor.set_params(owner, pk=1)
    result = await interactor.execute()

    repo.fetch_tag.assert_called_with(owner=owner, pk=1)
    assert result == expected


@pytest.mark.interactors
async def test_update_name(loop, owner):
    tag = Tag('Food', owner)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(tag)

    update = asyncio.Future(loop=loop)
    update.set_result(True)

    repo = mock.MagicMock()
    repo.fetch_tag = mock.MagicMock(return_value=fetch)
    repo.update_tag = mock.MagicMock(return_value=update)

    interactor = tags.UpdateTagInteractor(repo)
    interactor.set_params(owner, 1, {'name': 'Meals'})
    updated = await interactor.execute()

    repo.fetch_tag.assert_called_with(owner, 1)
    repo.update_tag.assert_called_with(tag, ['name'])

    assert updated.name == 'Meals'

@pytest.mark.interactors
async def test_update_name_failed(loop, owner):
    tag = Tag('Food', owner)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(tag)

    repo = mock.MagicMock()
    repo.fetch_tag = mock.MagicMock(return_value=fetch)
    repo.update_tag = mock.MagicMock(side_effect=EntityAlreadyExist)

    interactor = tags.UpdateTagInteractor(repo)
    interactor.set_params(owner, 1, {'name': 'Meals'})

    with pytest.raises(ValidationError):
        await interactor.execute()

    repo.fetch_tag.assert_called_with(owner, 1)
    repo.update_tag.assert_called_with(tag, ['name'])


@pytest.mark.interactors
@pytest.mark.parametrize('expected', (True, False))
async def test_remove_tag(loop, owner, expected):
    tag = Tag('Food', owner)

    fetch = asyncio.Future(loop=loop)
    fetch.set_result(tag)

    remove = asyncio.Future(loop=loop)
    remove.set_result(expected)

    repo = mock.MagicMock()
    repo.fetch_tag = mock.MagicMock(return_value=fetch)
    repo.remove_tag = mock.MagicMock(return_value=remove)

    interactor = tags.RemoveTagInteractor(repo)
    interactor.set_params(owner, 1)
    removed = await interactor.execute()

    repo.fetch_tag.assert_called_with(owner, 1)
    repo.remove_tag.assert_called_with(tag)
    assert removed == expected
