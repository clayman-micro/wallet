from datetime import datetime

import pytest

from wallet.entities import EntityAlreadyExist, EntityNotFound, Tag
from wallet.repositories.tags import TagsRepository


async def save_tag(tag, conn):
    query = """
        INSERT INTO tags (name, enabled, owner_id, created_on)
        VALUES ($1, $2, $3, $4)
        RETURNING id
    """
    pk = await conn.fetchval(query, tag.name, tag.enabled, tag.owner.pk,
                             tag.created_on)
    return pk


@pytest.mark.repositories
@pytest.mark.parametrize('tags, expected', (
    ((), 0),
    ((('Foo', False), ), 0),
    ((('Foo', True), ('Bar', False)), 1),
    ((('Foo', True), ('Bar', True)), 2),
))
async def test_fetch_tags(client, owner, tags, expected):
    now = datetime.now()

    async with client.server.app.db.acquire() as conn:
        for name, enabled in tags:
            tag = Tag(name, owner, enabled=enabled, created_on=now)
            tag.pk = await save_tag(tag, conn)

        repo = TagsRepository(conn=conn)
        result = await repo.fetch(owner)

    assert len(result) == expected


@pytest.mark.repositories
@pytest.mark.parametrize('tags, expected', (
    ((), 0),
    ((('Foo', False), ), 0),
    ((('Foo', True), ('Bar', False)), 1),
    ((('Foo', True), ('Bar', True)), 1),
    ((('Foo', True), ('Foe', True), ('Bar', True)), 2),
))
async def test_fetch_tags_by_name(client, owner, tags, expected):
    now = datetime.now()
    async with client.server.app.db.acquire() as conn:
        for name, enabled in tags:
            tag = Tag(name, owner, enabled=enabled, created_on=now)
            tag.pk = await save_tag(tag, conn)

        repo = TagsRepository(conn=conn)
        result = await repo.fetch(owner, name='Fo')

    assert len(result) == expected


@pytest.mark.repositories
async def test_fetch_tag(client, owner):
    now = datetime.now()
    async with client.server.app.db.acquire() as conn:
        for name, enabled in (('Foo', True), ('Bar', True)):
            tag = Tag(name, owner, enabled=enabled, created_on=now)
            tag.pk = await save_tag(tag, conn)

        repo = TagsRepository(conn=conn)
        tag = await repo.fetch_tag(owner, 1)

    assert isinstance(tag, Tag)
    assert tag.pk == 1
    assert tag.name == 'Foo'


@pytest.mark.repositories
async def test_fetch_tag_failed(client, owner):
    async with client.server.app.db.acquire() as conn:
        repo = TagsRepository(conn=conn)

        with pytest.raises(EntityNotFound):
            await repo.fetch_tag(owner, 1)


@pytest.mark.repositories
async def test_save_tag(client, owner):
    async with client.server.app.db.acquire() as conn:
        tag = Tag('Foo', owner, created_on=datetime.now())

        repo = TagsRepository(conn=conn)
        pk = await repo.save_tag(tag)

    assert pk == 1


@pytest.mark.repositories
async def test_save_tag_failed(client, owner):
    now = datetime.now()
    async with client.server.app.db.acquire() as conn:
        for name, enabled in (('Foo', True), ('Bar', True)):
            tag = Tag(name, owner, enabled=enabled, created_on=now)
            tag.pk = await save_tag(tag, conn)

        tag = Tag('Foo', owner)

        repo = TagsRepository(conn=conn)
        with pytest.raises(EntityAlreadyExist):
            await repo.save_tag(tag)


@pytest.mark.repositories
async def test_update_tag(client, owner):
    now = datetime.now()
    async with client.server.app.db.acquire() as conn:
        for name, enabled in (('Foo', True), ('Bar', True)):
            tag = Tag(name, owner, enabled=enabled, created_on=now)
            tag.pk = await save_tag(tag, conn)

        tag.name = 'Baz'

        repo = TagsRepository(conn=conn)
        updated = await repo.update_tag(tag, ('name', ))

    assert updated


@pytest.mark.repositories
async def test_update_tag_failed(client, owner):
    now = datetime.now()
    async with client.server.app.db.acquire() as conn:
        for name, enabled in (('Foo', True), ('Bar', True)):
            tag = Tag(name, owner, enabled=enabled, created_on=now)
            tag.pk = await save_tag(tag, conn)

        tag.name = 'Foo'

        repo = TagsRepository(conn=conn)
        with pytest.raises(EntityAlreadyExist):
            await repo.update_tag(tag, ('name', ))


@pytest.mark.repositories
@pytest.mark.parametrize('enabled, expected', (
    (True, True),
    (False, False)
))
async def test_remove_tag(client, owner, enabled, expected):
    now = datetime.now()
    async with client.server.app.db.acquire() as conn:
        for name, enabled in (('Foo', enabled), ('Bar', enabled)):
            tag = Tag(name, owner, enabled=enabled, created_on=now)
            tag.pk = await save_tag(tag, conn)

        repo = TagsRepository(conn=conn)
        removed = await repo.remove_tag(tag)

    assert removed == expected
