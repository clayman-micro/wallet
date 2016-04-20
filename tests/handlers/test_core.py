import pytest


@pytest.mark.run_loop
async def test_index(client):
    async with client.request('GET', endpoint='core.index') as response:
        assert response.status == 200

        result = await response.text()
        assert 'wallet' in result
