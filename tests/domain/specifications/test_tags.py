import asyncio
from unittest import mock

import pytest

from wallet.domain import EntityAlreadyExist
from wallet.domain.entities import Tag
from wallet.domain.specifications import UniqueTagNameSpecification
from wallet.domain.storage import TagsRepo


async def test_tag_name_available(tag: Tag) -> None:
    find = asyncio.Future()
    find.set_result([])

    repo = TagsRepo()
    repo.find = mock.MagicMock(return_value=find)

    spec = UniqueTagNameSpecification(repo)
    result = await spec.is_satisfied_by(tag)

    assert result


async def test_tag_name_should_be_unique(tag: Tag) -> None:
    tag.key = 1

    find = asyncio.Future()
    find.set_result([tag])

    repo = TagsRepo()
    repo.find = mock.MagicMock(return_value=find)

    spec = UniqueTagNameSpecification(repo)

    with pytest.raises(EntityAlreadyExist):
        t = Tag(tag.name, tag.user)
        await spec.is_satisfied_by(t)

    repo.find.assert_called_once()
