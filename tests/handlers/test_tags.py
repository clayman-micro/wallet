from datetime import datetime

import pytest

from tests.handlers import prepare_request

from wallet import App  # noqa
from wallet.storage.tags import add_tag


@pytest.mark.handlers
@pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
@pytest.mark.parametrize('method,endpoint,parts', (
    ('GET', 'api.tags.get_tags', None),
    ('POST', 'api.tags.create_tag', None),
    ('GET', 'api.tags.get_tag', {'instance_id': 1}),
    ('PUT', 'api.tags.update_tag', {'instance_id': 1}),
    ('DELETE', 'api.tags.remove_tag', {'instance_id': 1}),
))
async def test_unauthorized(client, passport, headers, method, endpoint, parts):
    app: App = client.server.app
    app.config['passport_dsn'] = passport

    if parts:
        url = app.router.named_resources()[endpoint].url(parts=parts)
    else:
        url = app.router.named_resources()[endpoint].url()

    call_method = getattr(client, method.lower())
    resp = await call_method(url, headers=headers)

    assert resp.status == 401


@pytest.mark.handlers
async def test_get_tags(client, passport, owner):
    app: App = client.server.app
    app.config['passport_dsn'] = passport

    now = datetime.now()
    async with app.db.acquire() as conn:
        await add_tag(owner, 'Foo', now, conn)

    url = app.router.named_resources()['api.tags.get_tags'].url()
    resp = await client.get(url, headers={'X-ACCESS-TOKEN': owner['token']})

    assert resp.status == 200
    result = await resp.json()
    assert result['tags'] == [{'id': 1, 'name': 'Foo'}]


@pytest.mark.handlers
async def test_get_tags_with_filter(client, passport, owner):
    app: App = client.server.app
    app.config['passport_dsn'] = passport

    now = datetime.now()
    async with app.db.acquire() as conn:
        for tag in ('Foo', 'Bar', 'Baz'):
            await add_tag(owner, tag, now, conn)

    url = app.router.named_resources()['api.tags.get_tags'].url()
    resp = await client.get(f'{url}?name=F',
                            headers={'X-ACCESS-TOKEN': owner['token']})

    assert resp.status == 200
    result = await resp.json()
    assert result['tags'] == [{'id': 1, 'name': 'Foo'}]
    assert result['meta'] == {'total': 1, 'search': {'name': 'F'}}


@pytest.mark.handlers
@pytest.mark.parametrize('json', [True, False])
async def test_create_success(client, passport, owner, json):
    app: App = client.server.app
    app.config['passport_dsn'] = passport

    data = {'name': 'Foo'}

    url = app.router.named_resources()['api.tags.create_tag'].url()
    resp = await client.post(url, **prepare_request(
        data, {'X-ACCESS-TOKEN': owner['token']}, json
    ))

    assert resp.status == 201
    result = await resp.json()
    assert result['tag'] == {'id': 1, 'name': 'Foo'}


@pytest.mark.handlers
@pytest.mark.parametrize('json', [True, False])
async def test_create_with_name_conflict(client, passport, owner, json):
    app: App = client.server.app
    app.config['passport_dsn'] = passport

    now = datetime.now()
    async with app.db.acquire() as conn:
        await add_tag(owner, 'Foo', now, conn)

    data = {'name': 'Foo'}

    url = app.router.named_resources()['api.tags.create_tag'].url()
    resp = await client.post(url, **prepare_request(
        data, {'X-ACCESS-TOKEN': owner['token']}, json
    ))

    assert resp.status == 400


@pytest.mark.handlers
@pytest.mark.parametrize('method, endpoint', (
    ('GET', 'api.tags.get_tag'),
    ('PUT', 'api.tags.update_tag'),
    ('DELETE', 'api.tags.remove_tag'),
))
async def test_missing(client, passport, owner, method, endpoint):
    app: App = client.server.app
    app.config['passport_dsn'] = passport

    url = app.router.named_resources()[endpoint].url(parts={
        'instance_id': 1
    })
    call_method = getattr(client, method.lower())
    resp = await call_method(url, headers={'X-ACCESS-TOKEN': owner['token']})

    assert resp.status == 404


@pytest.mark.handlers
async def test_get_tag(client, passport, owner):
    app: App = client.server.app
    app.config['passport_dsn'] = passport

    now = datetime.now()
    async with app.db.acquire() as conn:
        for tag in ('Foo', 'Bar', 'Baz'):
            await add_tag(owner, tag, now, conn)

    url = app.router.named_resources()['api.tags.get_tag'].url(
        parts={'instance_id': 1})
    resp = await client.get(url, headers={'X-ACCESS-TOKEN': owner['token']})

    assert resp.status == 200
    result = await resp.json()
    assert result['tag'] == {'id': 1, 'name': 'Foo'}


@pytest.mark.handlers
@pytest.mark.parametrize('json', (True, False))
async def test_update_tag(client, passport, owner, json):
    app: App = client.server.app
    app.config['passport_dsn'] = passport

    now = datetime.now()
    async with app.db.acquire() as conn:
        for tag in ('Foo', 'Bar', 'Baz'):
            await add_tag(owner, tag, now, conn)

    data = {'name': 'Fooo'}

    url = app.router.named_resources()['api.tags.update_tag'].url(
        parts={'instance_id': 1})
    resp = await client.put(url, **prepare_request(
        data, {'X-ACCESS-TOKEN': owner['token']}, json
    ))

    assert resp.status == 200
    result = await resp.json()
    assert result['tag'] == {'id': 1, 'name': 'Fooo'}


@pytest.mark.handlers
@pytest.mark.parametrize('json', (True, False))
async def test_update_tag_with_conflict_name(client, passport, owner, json):
    app: App = client.server.app
    app.config['passport_dsn'] = passport

    now = datetime.now()
    async with app.db.acquire() as conn:
        for tag in ('Foo', 'Bar', 'Baz'):
            await add_tag(owner, tag, now, conn)

    data = {'name': 'Bar'}

    url = app.router.named_resources()['api.tags.update_tag'].url(
        parts={'instance_id': 1})
    resp = await client.put(url, **prepare_request(
        data, {'X-ACCESS-TOKEN': owner['token']}, json
    ))

    assert resp.status == 400


@pytest.mark.handlers
@pytest.mark.parametrize('json', (True, False))
async def test_remove_tag(client, passport, owner, json):
    app: App = client.server.app
    app.config['passport_dsn'] = passport

    now = datetime.now()
    async with app.db.acquire() as conn:
        for tag in ('Foo', 'Bar', 'Baz'):
            await add_tag(owner, tag, now, conn)

    url = app.router.named_resources()['api.tags.remove_tag'].url(
        parts={'instance_id': 1})
    resp = await client.delete(url, headers={'X-ACCESS-TOKEN': owner['token']})

    assert resp.status == 200
