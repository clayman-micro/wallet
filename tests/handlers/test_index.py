import pkg_resources
import pytest


@pytest.mark.handlers
async def test_index(client, passport_gateway):
    client.server.app.passport = passport_gateway
    access_token = 'access-token'

    resp = await client.get('/', headers={'X-ACCESS-TOKEN': access_token})
    assert resp.status == 200
    assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'

    data = await resp.json()
    assert data == {
        'project': pkg_resources.get_distribution('wallet').project_name,
        'version': pkg_resources.get_distribution('wallet').version
    }
