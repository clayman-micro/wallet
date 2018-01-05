from datetime import datetime
from decimal import Decimal

import pytest
from tests.handlers import prepare_request


@pytest.fixture(scope='module')
def add_account():
    async def create(name, owner, app):
        async with app.db.acquire() as conn:
            query = """
                INSERT INTO accounts (name, enabled, owner_id, created_on)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """
            account_id = await conn.fetchval(query, name, True, owner.pk,
                                             datetime.now())
            return account_id
    return create


@pytest.fixture(scope='module')
def add_operation():
    async def create(amount, owner, account, app):
        async with app.db.acquire() as conn:
            query = """
                INSERT INTO operations (
                    type, amount, account_id, enabled, owner_id, created_on
                )
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """
            operation_id = await conn.fetchval(
                query, 'expense', amount, account, True, owner.pk,
                datetime.now()
            )
        return operation_id
    return create


@pytest.mark.handlers
@pytest.mark.parametrize('qs, expected', (
    ('', 200),
    ('year=2017&month=11', 200),
    ('year=2017', 422),
    ('month=13', 422),
    ('year=17&month=1', 422)
))
async def test_get_operations(client, owner, passport_gateway, add_account, qs,
                              expected):
    app = client.server.app
    app.passport = passport_gateway

    account_id = await add_account('Visa', owner, app)

    url = app.router.named_resources()['api.get_operations'].url(parts={
        'account': account_id
    })
    path = '?'.join((url, qs))
    resp = await client.get(path, headers={'X-ACCESS-TOKEN': 'foo'})
    assert resp.status == expected


@pytest.mark.handlers
@pytest.mark.parametrize('json', (True, False))
@pytest.mark.parametrize('payload, expected', (
    ({'amount': '1000'}, 201),
    ({'amount': '1000', 'description': 'Meal', 'type': 'expense'}, 201),
    ({'amount': '25000', 'description': 'Salary', 'type': 'income'}, 201),
    ({'amount': '25000', 'description': 'Salary', 'type': 'income',
      'created_on': '2017-12-12T00:00:00'}, 201),

    ({'amount': 'foo'}, 422),
    ({'amount': '1000', 'type': 'foo'}, 422),
    ({'amount': '1000', 'type': 'income', 'created_on': 'foo'}, 422),
    ({'amount': '1000', 'type': 'income', 'created_on': '2017-12-12'}, 422),
))
async def test_add_operation(client, owner, passport_gateway, add_account,
                             json, payload, expected):
    app = client.server.app
    app.passport = passport_gateway

    account_id = await add_account('Visa', owner, app)

    url = app.router.named_resources()['api.add_operation'].url(parts={
        'account': account_id
    })
    resp = await client.post(url, **prepare_request(payload, 'foo', json))

    print(await resp.json())
    assert resp.status == expected


@pytest.mark.handlers
async def test_get_operation(client, owner, passport_gateway, add_account,
                             add_operation):
    app = client.server.app
    app.passport = passport_gateway

    account_id = await add_account('Visa', owner, app)
    operation_id = await add_operation(Decimal(100.0), owner, account_id, app)

    url = app.router.named_resources()['api.get_operation'].url(parts={
        'account': account_id,
        'operation': operation_id
    })
    resp = await client.get(url, headers={'X-ACCESS-TOKEN': 'foo'})
    assert resp.status == 200


@pytest.mark.handlers
async def test_remove_operation(client, owner, passport_gateway, add_account,
                                add_operation):
    app = client.server.app
    app.passport = passport_gateway

    account_id = await add_account('Visa', owner, app)
    operation_id = await add_operation(Decimal(100.0), owner, account_id, app)

    url = app.router.named_resources()['api.remove_operation'].url(parts={
        'account': account_id,
        'operation': operation_id
    })
    resp = await client.delete(url, headers={'X-ACCESS-TOKEN': 'foo'})
    assert resp.status == 200
