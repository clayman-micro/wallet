import pytest


class TestCoreHandler(object):

    @pytest.mark.run_loop
    async def test_index(self, server, client):
        async with client.request('GET', endpoint='core.index') as response:
            assert response.status == 200

            result = await response.text()
            assert 'wallet' in result
