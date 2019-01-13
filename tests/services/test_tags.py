import asyncio
from unittest import mock

import pytest  # type: ignore

from wallet.domain import Tag
from wallet.domain.storage import EntityAlreadyExist
from wallet.services.tags import TagsService, TagValidator
from wallet.validation import ValidationError


class TestAccountValidator:
    @pytest.mark.unit
    def test_valid_payload(self, fake):
        validator = TagValidator()
        result = validator.validate_payload({"name": fake.safe_color_name()})
        assert result is not None

    @pytest.mark.unit
    @pytest.mark.parametrize("payload", ({}, {"name": ""}, {"foo": "bar"}))
    def test_invalid_payload(self, payload):
        with pytest.raises(ValidationError):
            validator = TagValidator()
            validator.validate_payload(payload)


class TestTagsService:
    @pytest.mark.unit
    async def test_add_tag(self, fake, user, storage):
        name = fake.safe_color_name()

        add = asyncio.Future()
        add.set_result(1)

        find = asyncio.Future()
        find.set_result([])

        storage.tags.add = mock.MagicMock(return_value=add)
        storage.tags.find_by_name = mock.MagicMock(return_value=find)

        service = TagsService(storage)
        tag = await service.add(name, user)

        storage.tags.add.assert_called()
        assert tag == Tag(key=1, name=name, user=user)

    @pytest.mark.unit
    async def test_reject_tag_with_duplicate_name(self, fake, user, storage):
        name = fake.safe_color_name()

        find = asyncio.Future()
        find.set_result([Tag(key=1, name=name, user=user)])

        storage.tags.find_by_name = mock.MagicMock(return_value=find)

        with pytest.raises(EntityAlreadyExist):
            service = TagsService(storage)
            await service.add(name, user)

        storage.tags.find_by_name.assert_called()
