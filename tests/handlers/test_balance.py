import pytest

from wallet.storage import accounts, transactions

from . import create_owner, create_account, create_category


# TODO: need to rewrite this tests


@pytest.mark.balance
@pytest.mark.run_loop
@pytest.mark.parametrize('tr_type,amount,expected', (
    (transactions.INCOME_TRANSACTION, 100, {'income': 100.0, 'expense': 0.0}),
    (transactions.EXPENSE_TRANSACTION, 300, {'income': 0.0, 'expense': 300.0}),
))
async def test_balance_after_add_transaction(app, client, owner, tr_type,
                                             amount, expected):
    account = await create_account({
        'name': 'Credit card', 'original_amount': 30000.0,
        'owner_id': owner['id']
    }, app=app)
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app)

    params = await client.get_params('api.create_transaction',
                                     owner['credentials'])
    params.update(data={
        'description': 'Meal', 'amount': amount, 'type': tr_type,
        'account_id': account['id'], 'category_id': category['id'],
        'created_on': '2015-08-20T00:00:00'
    })
    async with client.request('POST', **params) as response:
        assert response.status == 201

    params = await client.get_params('api.get_balance', owner['credentials'])
    params['endpoint_params'] = {'account_id': account['id']}
    async with client.request('GET', **params) as response:
        assert response.status == 200
        data = await response.json()
        assert 'balance' in data
        assert data['balance'][0] == {
            'remain': 30000.0, 'date': '2015-08-01T00:00:00', **expected
        }


@pytest.mark.balance
@pytest.mark.run_loop
@pytest.mark.parametrize('tr_type,before,after,expected', (
    (transactions.INCOME_TRANSACTION, 100, 1000, {'income': 1000.0,
                                                  'expense': 0.0}),
    (transactions.EXPENSE_TRANSACTION, 300, 3000, {'income': 0.0,
                                                   'expense': 3000.0})
))
async def test_balance_after_update_transaction(app, client, owner, tr_type,
                                                before, after, expected):
    account = await create_account({
        'name': 'Credit card', 'original_amount': 30000.0,
        'owner_id': owner['id']
    }, app=app)
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app)

    params = await client.get_params('api.create_transaction',
                                     owner['credentials'])
    params.update(data={
        'description': 'Meal', 'amount': before, 'type': tr_type,
        'account_id': account['id'], 'category_id': category['id'],
        'created_on': '2015-08-20T00:00:00'
    })
    async with client.request('POST', **params) as response:
        assert response.status == 201
        data = await response.json()
        transaction_id = data['transaction']['id']

    params.update(endpoint='api.update_transaction', data={'amount': after},
                  endpoint_params={'instance_id': transaction_id})
    async with client.request('PUT', **params) as response:
        assert response.status == 200

    params = await client.get_params('api.get_balance', owner['credentials'])
    params['endpoint_params'] = {'account_id': account['id']}
    async with client.request('GET', **params) as response:
        assert response.status == 200
        data = await response.json()
        assert 'balance' in data
        assert data['balance'][0] == {
            'remain': 30000.0, 'date': '2015-08-01T00:00:00', **expected
        }


@pytest.mark.balance
@pytest.mark.run_loop
@pytest.mark.parametrize('tr_type,amount', (
    (transactions.INCOME_TRANSACTION, 10000),
    (transactions.EXPENSE_TRANSACTION, 300),
))
async def balance_after_remove_transaction(app, client, owner, tr_type, amount):
    account = await create_account({
        'name': 'Credit card', 'original_amount': 30000.0,
        'owner_id': owner['id']
    }, app=app)
    category = await create_category({'name': 'Food', 'owner_id': owner['id']},
                                     app)

    params = await client.get_params('api.create_transaction',
                                     owner['credentials'])
    params.update(data={
        'description': 'Meal', 'amount': amount, 'type': tr_type,
        'account_id': account['id'], 'category_id': category['id'],
        'created_on': '2015-08-20T00:00:00'
    })
    async with client.request('POST', **params) as response:
        assert response.status == 201
        data = await response.json()
        transaction_id = data['transaction']['id']

    params.update(endpoint='api.remove_transaction', endpoint_params={
        'instance_id': transaction_id
    })
    async with client.request('DELETE', **params) as response:
        text = await response.text()
        print(text)
        assert response.status == 200

    params = await client.get_params('api.get_balance', owner['credentials'])
    params['endpoint_params'] = {'account_id': account['id']}
    async with client.request('GET', **params) as response:
        assert response.status == 200
        data = await response.json()
        assert 'balance' in data
        print(data['balance'])
        assert data['balance'][0] == {
            'remain': 30000.0, 'expense': 0.0, 'income': 0.0,
            'date': '2015-08-01T00:00:00'
        }
