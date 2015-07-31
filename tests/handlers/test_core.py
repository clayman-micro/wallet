import pytest

from tests.conftest import async_test


class TestCoreHandler(object):

    @pytest.mark.handlers
    @async_test()
    def test_index(self, application, server):
        url = server.reverse_url('core.index')
        with (yield from server.response_ctx('GET', url=url)) as response:
            assert response.status == 200

            result = yield from response.text()
            assert 'wallet' in result
