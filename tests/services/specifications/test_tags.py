import asyncio
from unittest import mock

import pytest  # type: ignore

from wallet.domain import EntityAlreadyExist
from wallet.domain.entities import Tag
from wallet.domain.specifications import UniqueTagNameSpecification


@pytest.mark.unit
async def test_tag_name_available(tags_repo, tag: Tag) -> None:
    find: asyncio.Future = asyncio.Future()
    find.set_result([])

    tags_repo.find = mock.MagicMock(return_value=find)

    spec = UniqueTagNameSpecification(tags_repo)
    result = await spec.is_satisfied_by(tag)

    assert result


@pytest.mark.unit
async def test_tag_name_should_be_unique(tags_repo, tag: Tag) -> None:
    find: asyncio.Future = asyncio.Future()
    find.set_result([tag])

    tags_repo.find = mock.MagicMock(return_value=find)

    spec = UniqueTagNameSpecification(tags_repo)

    with pytest.raises(EntityAlreadyExist):
        t = Tag(2, tag.name, tag.user)
        await spec.is_satisfied_by(t)

    tags_repo.find.assert_called_once()
