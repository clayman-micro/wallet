import pytest

from tests.conftest import async_test


class TestCoreHandler(object):

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_index(self, application, **kwargs):
        server = kwargs.get('server')

        with (yield from server.response_ctx('GET')) as response:
            assert response.status == 200

            result = yield from response.text()
            assert 'wallet' in result