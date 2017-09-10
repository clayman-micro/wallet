from datetime import datetime

import pytest

from wallet import App  # noqa
from wallet.storage import AlreadyExist, ResourceNotFound
from wallet.storage.tags import (fetch_tag, fetch_tags, add_tag, rename_tag,
                                 remove_tag)


@pytest.mark.storage
@pytest.mark.parametrize('tags,expected', (
    ((), []),
    ((('Bar', False), ), []),
    ((('Foo', True), ('Bar', False)), [{'id': 1, 'name': 'Foo'}]),
    ((('Foo', True), ('Baz', True)),
     [{'id': 1, 'name': 'Foo'}, {'id': 2, 'name': 'Baz'}])
))
async def test_fetch_tags(client, tags, expected):
    app: App = client.server.app

    now = datetime.now()

    async with app.db.acquire() as conn:
        query = """
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        for name, enabled in tags:
            await conn.execute(query, name, enabled, 1, now)

    async with app.db.acquire() as conn:
        tags = await fetch_tags({'id': 1}, conn)

    assert tags == expected


@pytest.mark.storage
async def test_fetch_tag_success(client):
    app: App = client.server.app

    now = datetime.now()
    async with app.db.acquire() as conn:
        query = """
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        for name, enabled in (('Foo', True), ('Bar', False)):
            await conn.execute(query, name, enabled, 1, now)

    async with app.db.acquire() as conn:
        tag = await fetch_tag({'id': 1}, 1, conn)

    assert tag == {'id': 1, 'name': 'Foo'}


@pytest.mark.storage
async def test_fetch_tag_failed(client):
    app: App = client.server.app

    async with app.db.acquire() as conn:
        with pytest.raises(ResourceNotFound):
            await fetch_tag({'id': 1}, 1, conn)


@pytest.mark.storage
async def test_add_tag_success(client):
    app: App = client.server.app

    now = datetime.now()
    async with app.db.acquire() as conn:
        tag = await add_tag({'id': 1}, 'Foo', now, conn)

    assert tag == {'id': 1, 'name': 'Foo'}


@pytest.mark.storage
async def test_add_tag_failed(client):
    app: App = client.server.app

    now = datetime.now()
    owner = {'id': 1}
    async with app.db.acquire() as conn:
        query = """
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        await conn.execute(query, 'Foo', True, owner['id'], now)

        with pytest.raises(AlreadyExist):
            await add_tag({'id': 1}, 'Foo', now, conn)


@pytest.mark.storage
@pytest.mark.parametrize('tags', (
    (('Foo', True), ),
    (('Foo', True), ('Bar', False))
))
async def test_rename_tag_success(client, tags):
    app: App = client.server.app

    now = datetime.now()
    async with app.db.acquire() as conn:
        query = """
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        for name, enabled in tags:
            await conn.execute(query, name, enabled, 1, now)

        success = await rename_tag({'id': 1}, {'id': 1}, 'Bar', conn)
        assert success

        query = 'SELECT name from tags WHERE id = $1 AND owner_id = $2'
        tag_name = await conn.fetchval(query, 1, 1)
        assert tag_name == 'Bar'


@pytest.mark.storage
async def test_rename_tag_failed(client):
    app: App = client.server.app

    now = datetime.now()
    async with app.db.acquire() as conn:
        query = """
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        for name, enabled in (('Foo', True), ('Bar', True)):
            await conn.execute(query, name, enabled, 1, now)

        with pytest.raises(AlreadyExist):
            await rename_tag({'id': 1}, {'id': 1}, 'Bar', conn)


@pytest.mark.storage
@pytest.mark.parametrize('tags,expected', (
    ((('Foo', True), ('Bar', True)), True),
    ((('Foo', False), ('Bar', True)), False),
))
async def test_remove_tag_success(client, tags, expected):
    app: App = client.server.app

    now = datetime.now()
    async with app.db.acquire() as conn:
        query = """
            INSERT INTO tags (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        for name, enabled in tags:
            await conn.execute(query, name, enabled, 1, now)

        removed = await remove_tag({'id': 1}, {'id': 1}, conn)
        assert removed == expected

        query = 'SELECT COUNT(id) from tags WHERE id = $1 AND owner_id = $2 AND enabled = TRUE'  # noqa
        count = await conn.fetchval(query, 1, 1)
        assert count == 0
