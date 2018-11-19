import asyncio
from unittest import mock

import pytest  # type: ignore

from wallet.domain import EntityAlreadyExist
from wallet.domain.entities import Tag
from wallet.services.tags import TagsService


class TestTagsService:

    @pytest.mark.unit
    async def test_add_tag(self, fake, user, storage):
        name = fake.safe_color_name()

        add = asyncio.Future()
        add.set_result(1)

        storage.tags.add = mock.MagicMock(return_value=add)

        service = TagsService(storage)
        tag = await service.add(name, user)

        storage.tags.add.assert_called()
        assert tag == Tag(key=1, name=name, user=user)

    @pytest.mark.unit
    async def test_reject_tag_with_duplicate_name(self, fake, user, storage):
        name = fake.safe_color_name()

        find = asyncio.Future()
        find.set_result([Tag(key=1, name=name, user=user)])

        storage.tags.find = mock.MagicMock(return_value=find)

        with pytest.raises(EntityAlreadyExist):
            service = TagsService(storage)
            await service.add(name, user)

        storage.tags.find.assert_called()
