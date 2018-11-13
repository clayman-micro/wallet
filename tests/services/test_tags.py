import pytest  # type: ignore

from wallet.domain import EntityAlreadyExist
from wallet.domain.commands import AddTag
from wallet.domain.entities import Tag
from wallet.services.tags import AddTagHandler


@pytest.mark.unit
async def test_add_tag(fake, user, storage):
    name = fake.safe_color_name()

    cmd = AddTag(name, user=user)
    handler = AddTagHandler(storage)
    await handler.handle(cmd)

    assert storage.tags.entities[user.key] == [Tag(0, name, user)]
    assert storage.was_committed


@pytest.mark.unit
async def test_add_existed_tag(fake, user, storage):
    name = fake.safe_color_name()

    tag = Tag(1, name, user)
    await storage.tags.add(tag)

    with pytest.raises(EntityAlreadyExist):
        cmd = AddTag(name, user)
        handler = AddTagHandler(storage)
        await handler.handle(cmd)
