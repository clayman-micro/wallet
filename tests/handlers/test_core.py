from aiohttp import request
import pytest

from tests.conftest import create_server, async_test


class TestCoreHandler(object):

    @pytest.mark.handlers
    @async_test
    def test_index(self, application):
        srv, url = yield from create_server(application)
        resp = yield from request('GET', url, loop=application.loop)
        assert resp.status == 200

        result = yield from resp.text()
        assert 'wallet' in result