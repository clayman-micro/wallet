from datetime import datetime

import pytest

from wallet.storage import transactions, details

from . import (create_owner, create_account, create_category,
               create_transaction, create_detail)


@pytest.mark.run_loop
@pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
@pytest.mark.parametrize('method, endpoint, endpoint_params', [
    ('GET', 'api.get_transactions', None),
    ('POST', 'api.create_transaction', None),
    ('GET', 'api.get_transaction', {'instance_id': 1}),
    ('PUT', 'api.update_transaction', {'instance_id': 1}),
    ('DELETE', 'api.remove_transaction', {'instance_id': 1})
])
async def test_unauthorized(client, headers, method, endpoint, endpoint_params):
    params = {'headers': headers, 'endpoint': endpoint,
              'endpoint_params': endpoint_params}
    async with client.request(method, **params) as response:
        assert response.status == 401


@pytest.mark.transactions
@pytest.mark.run_loop
async def test_collection(app, client, owner):
    account = await create_account({'name': 'Card', 'original_amount': 12345.67,
                                    'owner_id': owner['id']}, app=app)
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app=app)
    created_on = datetime.now()
    transaction = await create_transaction({
        'type': 'expense', 'description': 'Meal', 'amount': 270.0,
        'account_id': account['id'], 'category_id': category['id'],
        'created_on': created_on
    }, app)

    params = await client.get_params('api.get_transactions', owner['credentials'])
    async with client.request('GET', **params) as response:
        assert response.status == 200

        data = await response.json()
        assert 'transactions' in data
        assert data['transactions'] == [{
            'id': transaction['id'], 'type': 'expense', 'description': 'Meal',
            'amount': 270.0, 'account_id': account['id'],
            'category_id': category['id'],
            'created_on': created_on.strftime('%Y-%m-%dT%X')
        }, ]


@pytest.mark.transactions
@pytest.mark.run_loop
async def test_collection_for_stranger(app, client, stranger, transaction):
    params = await client.get_params('api.get_transactions',
                                     stranger['credentials'])
    async with client.request('GET', **params) as response:
        assert response.status == 200
        result = await response.json()
        assert 'transactions' in result
        assert len(result['transactions']) == 0


@pytest.mark.transactions
@pytest.mark.run_loop
@pytest.mark.parametrize('json', (True, False))
async def test_create(app, client, owner, json):
    account = await create_account({'name': 'Card', 'original_amount': 12345.67,
                                    'owner_id': owner['id']}, app=app)
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app=app)

    created_on = datetime.now().strftime('%Y-%m-%dT%X')
    params = await client.get_params('api.create_transaction', owner['credentials'])
    params.update(data={'type': 'expense', 'description': 'Meal',
                        'amount': 270.0, 'account_id': account['id'],
                        'category_id': category['id'],
                        'created_on': created_on}, json=json)

    async with client.request('POST', **params) as response:
        assert response.status == 201
        result = await response.json()
        assert 'transaction' in result
        assert result['transaction'] == {
            'id': 1, 'type': 'expense', 'description': 'Meal', 'amount': 270.0,
            'account_id': account['id'], 'category_id': category['id'],
            'created_on': created_on
        }


@pytest.mark.transactions
@pytest.mark.run_loop
@pytest.mark.parametrize('json', (True, False))
async def test_create_failed(app, client, owner, json):
    account = await create_account({'name': 'Card', 'original_amount': 12345.67,
                                    'owner_id': owner['id']}, app=app)

    created_on = datetime.now().strftime('%Y-%m-%dT%X')
    params = await client.get_params('api.create_transaction',
                                     owner['credentials'])
    params.update(data={'type': 'expense', 'description': 'Meal',
                        'amount': 270.0, 'account_id': account['id'],
                        'category_id': 1, 'created_on': created_on}, json=json)

    async with client.request('POST', **params) as response:
        assert response.status == 400
        result = await response.json()
        assert 'errors' in result
        assert 'category_id' in result['errors']


@pytest.mark.transactions
@pytest.mark.run_loop
@pytest.mark.parametrize('json', (True, False))
async def test_create_with_missing(app, client, owner, stranger, json):
    account = await create_account({'name': 'Card', 'original_amount': 12345.67,
                                    'owner_id': owner['id']}, app=app)
    category = await create_category({'name': 'Food',
                                      'owner_id': stranger['id']}, app=app)

    created_on = datetime.now().strftime('%Y-%m-%dT%X')
    params = await client.get_params('api.create_transaction',
                                     owner['credentials'])
    params.update(json=json, data={
        'type': 'expense', 'description': 'Meal',
        'amount': 270.0, 'account_id': account['id'],
        'category_id': category['id'], 'created_on': created_on
    })

    async with client.request('POST', **params) as response:
        assert response.status == 400
        result = await response.json()
        assert 'errors' in result
        assert 'category_id' in result['errors']


@pytest.mark.transactions
@pytest.mark.run_loop
@pytest.mark.parametrize('method, endpoint', (
    ('GET', 'api.get_transaction'),
    ('PUT', 'api.update_transaction'),
    ('DELETE', 'api.remove_transaction')
))
async def test_missing(client, owner, method, endpoint):
    params = await client.get_params(endpoint, owner['credentials'], 1)
    async with client.request(method, **params) as response:
        assert response.status == 404


@pytest.mark.transactions
@pytest.mark.run_loop
@pytest.mark.parametrize('method, endpoint', (
    ('GET', 'api.get_transaction'),
    ('PUT', 'api.update_transaction'),
    ('DELETE', 'api.remove_transaction')
))
async def test_access_for_stranger(client, transaction, stranger, method, endpoint):
    params = await client.get_params(endpoint, stranger['credentials'], transaction['id'])
    async with client.request(method, **params) as response:
        assert response.status == 404


@pytest.mark.transactions
@pytest.mark.run_loop
async def test_get_resource(app, client, owner):
    account = await create_account({'name': 'Card', 'original_amount': 12345.67,
                                    'owner_id': owner['id']}, app=app)
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app=app)
    created_on = datetime.now()
    transaction = await create_transaction({
        'type': 'expense', 'description': 'Meal', 'amount': 270.0,
        'account_id': account['id'], 'category_id': category['id'],
        'created_on': created_on}, app)

    params = await client.get_params('api.get_transaction',
                                     owner['credentials'], transaction['id'])
    async with client.request('GET', **params) as response:
        assert response.status == 200

        data = await response.json()
        assert 'transaction' in data
        assert data['transaction'] == {
            'id': transaction['id'], 'type': 'expense', 'description': 'Meal',
            'amount': 270.0, 'account_id': account['id'],
            'category_id': category['id'],
            'created_on': created_on.strftime('%Y-%m-%dT%X')
        }


@pytest.mark.transactions
@pytest.mark.run_loop
@pytest.mark.parametrize('json', (True, False))
async def test_update_resource(app, client, owner, json):
    account = await create_account({'name': 'Card', 'original_amount': 12345.67,
                                    'owner_id': owner['id']}, app=app)
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app=app)
    created_on = datetime.now()
    transaction = await create_transaction({
        'type': 'expense', 'description': 'Meal', 'amount': 270.0,
        'account_id': account['id'], 'category_id': category['id'],
        'created_on': created_on}, app)

    params = await client.get_params('api.update_transaction',
                                     owner['credentials'], transaction['id'])
    params.update(data={'amount': 300.0}, json=json)
    async with client.request('PUT', **params) as response:
        assert response.status == 200

        data = await response.json()
        assert 'transaction' in data
        assert data['transaction'] == {
            'id': transaction['id'], 'type': 'expense', 'description': 'Meal',
            'amount': 300.0, 'account_id': account['id'],
            'category_id': category['id'],
            'created_on': created_on.strftime('%Y-%m-%dT%X')
        }


@pytest.mark.transactions
@pytest.mark.run_loop
async def test_remove_resource(app, client, owner):
    account = await create_account({'name': 'Card', 'original_amount': 12345.67,
                                    'owner_id': owner['id']}, app=app)
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app=app)
    created_on = datetime.now()
    transaction = await create_transaction({
        'type': 'expense', 'description': 'Meal', 'amount': 270.0,
        'account_id': account['id'], 'category_id': category['id'],
        'created_on': created_on}, app)

    params = await client.get_params('api.remove_transaction', owner['credentials'],
                                     account['id'])

    async with client.request('DELETE', **params) as response:
        assert response.status == 200

    async with app['engine'].acquire() as conn:
        query = transactions.table.count().where(
            transactions.table.c.id == transaction['id'])
        count = await conn.scalar(query)
        assert count == 0
