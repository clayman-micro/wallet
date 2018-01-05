from datetime import datetime

import pytest
import ujson


def prepare_request(data, token, json=False):
    headers = {'X-ACCESS-TOKEN': token}
    if json:
        data = ujson.dumps(data)
        headers['Content-Type'] = 'application/json'

    return {'data': data, 'headers': headers}


@pytest.mark.handlers
async def test_get_accounts(client, passport_gateway):
    app = client.server.app
    app.passport = passport_gateway

    url = app.router.named_resources()['api.get_accounts'].url()
    resp = await client.get(url, headers={'X-ACCESS-TOKEN': 'foo'})
    assert resp.status == 200


@pytest.mark.handlers
@pytest.mark.parametrize('json', [True, False])
async def test_add_account(client, passport_gateway, json):
    app = client.server.app
    app.passport = passport_gateway

    data = {'name': 'Visa', 'amount': '0.0'}

    url = app.router.named_resources()['api.add_account'].url()
    resp = await client.post(url, **prepare_request(data, 'foo', json=json))
    assert resp.status == 201


@pytest.mark.handlers
@pytest.mark.parametrize('method, resource', (
    ('get', 'api.get_account'),
    ('put', 'api.update_account'),
    ('delete', 'api.remove_account')
))
async def test_missing_account(client, passport_gateway, method, resource):
    app = client.server.app
    app.passport = passport_gateway

    url = app.router.named_resources()[resource].url(parts={
        'instance_id': 1
    })

    do = getattr(client, method)
    resp = await do(url, headers={'X-ACCESS-TOKEN': 'foo'})
    assert resp.status == 404


@pytest.mark.handlers
async def test_get_account(client, owner, passport_gateway):
    app = client.server.app
    app.passport = passport_gateway

    async with app.db.acquire() as conn:
        query = """
            INSERT INTO accounts (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        await conn.execute(query, 'Visa', True, owner.pk, datetime.now())

    url = app.router.named_resources()['api.get_account'].url(parts={
        'instance_id': 1
    })

    resp = await client.get(url, headers={'X-ACCESS-TOKEN': 'foo'})
    assert resp.status == 200


@pytest.mark.handlers
@pytest.mark.parametrize('json', [True, False])
@pytest.mark.parametrize('payload', (
    {'name': 'Visa Classic'},
    {'original': '1000.0'},
    {'name': 'Visa Classic', 'original': '1000.0'}
))
async def test_update_account(client, owner, passport_gateway, payload, json):
    app = client.server.app
    app.passport = passport_gateway

    async with app.db.acquire() as conn:
        query = """
            INSERT INTO accounts (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        await conn.execute(query, 'Visa', True, owner.pk, datetime.now())

    url = app.router.named_resources()['api.update_account'].url(parts={
        'instance_id': 1
    })

    resp = await client.put(url, **prepare_request(payload, 'foo', json))
    assert resp.status == 200


@pytest.mark.handlers
async def test_remove_account(client, owner, passport_gateway):
    app = client.server.app
    app.passport = passport_gateway

    async with app.db.acquire() as conn:
        query = """
            INSERT INTO accounts (name, enabled, owner_id, created_on)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        await conn.execute(query, 'Visa', True, owner.pk, datetime.now())

    url = app.router.named_resources()['api.remove_account'].url(parts={
        'instance_id': 1
    })

    resp = await client.delete(url, headers={'X-ACCESS-TOKEN': 'foo'})
    assert resp.status == 200
