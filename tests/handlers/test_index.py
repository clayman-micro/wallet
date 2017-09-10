import pytest

from wallet import App  # noqa


@pytest.mark.handlers
async def test_index_handler(client, passport, owner):
    app: App = client.server.app
    app.config['passport_dsn'] = passport

    url = app.router.named_resources()['index'].url()
    resp = await client.get(url, headers={'X-ACCESS-TOKEN': owner['token']})

    assert resp.status == 200
