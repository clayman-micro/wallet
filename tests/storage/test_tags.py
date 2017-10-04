from datetime import datetime

import pytest

from wallet import App  # noqa
from wallet.storage import AlreadyExist, ResourceNotFound
from wallet.storage.owner import Owner
from wallet.storage.tags import (fetch_tag, fetch_tags, add_tag, rename_tag,
                                 remove_tag, Tag)


@pytest.mark.storage
@pytest.mark.parametrize('tags,expected', (
    ((), 0),
    ((('Bar', False), ), 0),
    ((('Foo', True), ('Bar', False)), 1),
    ((('Foo', True), ('Bar', True)), 2)
))
async def test_fetch_tags(client, tags, expected):
    app: App = client.server.app

    now = datetime.now()

    owner = Owner(1, 'foo@bar.baz')

    async with app.db.acquire() as conn:
        query = """
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        for name, enabled in tags:
            await conn.execute(query, name, enabled, owner.id, now)

    async with app.db.acquire() as conn:
        tags = await fetch_tags(owner, conn)

    assert len(tags) == expected


@pytest.mark.storage
async def test_fetch_tag_success(client):
    app: App = client.server.app

    owner = Owner(1, 'foo@bar.baz')

    now = datetime.now()
    async with app.db.acquire() as conn:
        query = """
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        for name, enabled in (('Foo', True), ('Bar', False)):
            await conn.execute(query, name, enabled, owner.id, now)

    async with app.db.acquire() as conn:
        tag = await fetch_tag(owner, 1, conn)

    assert isinstance(tag, Tag)
    assert tag.id == 1
    assert tag.name == 'Foo'


@pytest.mark.storage
async def test_fetch_tag_failed(client):
    app: App = client.server.app

    owner = Owner(1, 'foo@bar.baz')

    async with app.db.acquire() as conn:
        with pytest.raises(ResourceNotFound):
            await fetch_tag(owner, 1, conn)


@pytest.mark.storage
async def test_add_tag_success(client):
    app: App = client.server.app

    owner = Owner(1, 'foo@bar.baz')

    now = datetime.now()
    async with app.db.acquire() as conn:
        tag = await add_tag(owner, 'Foo', now, conn)

    assert isinstance(tag, Tag)
    assert tag.id == 1
    assert tag.name == 'Foo'


@pytest.mark.storage
async def test_add_tag_failed(client):
    app: App = client.server.app

    now = datetime.now()
    owner = Owner(1, 'foo@bar.baz')
    async with app.db.acquire() as conn:
        query = """
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        await conn.execute(query, 'Foo', True, owner.id, now)

        with pytest.raises(AlreadyExist):
            await add_tag(owner, 'Foo', now, conn)


@pytest.mark.storage
@pytest.mark.parametrize('tags', (
    (('Foo', True), ),
    (('Foo', True), ('Bar', False))
))
async def test_rename_tag_success(client, tags):
    app: App = client.server.app

    owner = Owner(1, 'foo@bar.baz')

    now = datetime.now()
    async with app.db.acquire() as conn:
        query = """
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """

        created = []
        for name, enabled in tags:
            tag = Tag(name, owner, enabled=enabled)
            tag.id = await conn.fetchval(query, tag.name, tag.enabled,
                                         tag.owner_id, now)
            created.append(tag)

        success = await rename_tag(created[0], 'Bar', conn)
        assert success

        query = 'SELECT name from tags WHERE id = $1 AND owner_id = $2'
        tag_name = await conn.fetchval(query, created[0].id, 1)
        assert tag_name == 'Bar'


@pytest.mark.storage
async def test_rename_tag_failed(client):
    app: App = client.server.app

    owner = Owner(1, 'foo@bar.baz')

    now = datetime.now()
    async with app.db.acquire() as conn:
        query = """
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        for name, enabled in (('Foo', True), ('Bar', True)):
            await conn.execute(query, name, enabled, owner.id, now)

        with pytest.raises(AlreadyExist):
            tag = Tag('Foo', owner, id=1)
            await rename_tag(tag, 'Bar', conn)


@pytest.mark.storage
@pytest.mark.parametrize('tags,expected', (
    ((('Foo', True), ('Bar', True)), True),
    ((('Foo', False), ('Bar', True)), False),
))
async def test_remove_tag_success(client, tags, expected):
    app: App = client.server.app

    owner = Owner(1, 'foo@bar.baz')

    now = datetime.now()
    async with app.db.acquire() as conn:
        query = """
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        created = []
        for name, enabled in tags:
            tag = Tag(name, owner, enabled=enabled)
            tag.id = await conn.fetchval(query, tag.name, tag.enabled,
                                         tag.owner_id, now)
            created.append(tag)

        removed = await remove_tag(created[0], conn)
        assert removed == expected

        query = 'SELECT COUNT(id) from tags WHERE id = $1 AND owner_id = $2 AND enabled = TRUE'  # noqa
        count = await conn.fetchval(query, created[0].id, 1)
        assert count == 0
