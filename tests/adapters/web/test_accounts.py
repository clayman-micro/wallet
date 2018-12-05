import pytest  # type: ignore
import ujson  # type: ignore

from wallet.validation import Validator


def prepare_request(data, headers=None, json=False):
    if headers is None:
        headers = {}

    if json:
        data = ujson.dumps(data)
        headers['Content-Type'] = 'application/json'

    return {'data': data, 'headers': headers}


@pytest.mark.integration
async def test_register_account_unauthorized(fake, aiohttp_client, app, passport):
    app['passport'] = passport
    client = await aiohttp_client(app)

    data = {'name': fake.credit_card_provider()}

    url = app.router.named_resources()['api.accounts.register'].url_for()
    resp = await client.post(url, **prepare_request(data, json=True))
    assert resp.status == 401


@pytest.mark.integration
async def test_register_account(fake, aiohttp_client, app, passport):
    app['passport'] = passport
    client = await aiohttp_client(app)

    data = {'name': fake.credit_card_provider()}

    url = app.router.named_resources()['api.accounts.register'].url_for()
    resp = await client.post(url, **prepare_request(data, {'X-ACCESS-TOKEN': 'token'}, json=True))

    assert resp.status == 201
    assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'

    validator = Validator(schema={
        'account': {'required': True, 'type': 'dict', 'schema': {
            'id': {'required': True, 'type': 'integer'},
            'name': {'required': True, 'type': 'string'}
        }}
    })

    result = await resp.json()
    assert validator.validate_payload(result)
