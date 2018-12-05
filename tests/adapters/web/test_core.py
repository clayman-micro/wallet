import pkg_resources
import pytest  # type: ignore


@pytest.mark.integration
async def test_index(aiohttp_client, app, passport):
    app['passport'] = passport
    client = await aiohttp_client(app)
    access_token = 'access-token'

    resp = await client.get('/', headers={'X-ACCESS-TOKEN': access_token})
    assert resp.status == 200
    assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'

    data = await resp.json()
    assert data == {
        'project': pkg_resources.get_distribution('wallet').project_name,
        'version': pkg_resources.get_distribution('wallet').version
    }
