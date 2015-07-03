import asyncio
from datetime import datetime

import pytest

from wallet.models.auth import users_table, encrypt_password

from tests.conftest import async_test


class TestRegistrationHandler(object):
    endpoint = 'auth.registration'

    @pytest.mark.handlers
    @pytest.mark.parametrize('params', [
        {'json': False},
        {'json': True}
    ])
    @async_test(attach_server=True)
    def test_success(self, application, db, params, **kwargs):
        server = kwargs.get('server')

        params.update(endpoint=self.endpoint,
                      data={'login': 'John', 'password': 'top-secret'})
        with (yield from server.response_ctx('POST', **params)) as response:
            print((yield from response.text()))
            assert response.status == 201

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_fail_without_password(self, application, db, **kwargs):
        server = kwargs.get('server')

        params = {
            'endpoint': self.endpoint,
            'data': {'login': 'John'},
            'json': True
        }
        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 400

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_fail_with_already_existed(self, application, db, **kwargs):
        server = kwargs.get('server')
        with (yield from application.engine) as conn:
            uid = yield from conn.scalar(users_table.insert().values(
                login='John', password='top-secret',
                created_on=datetime.now()))

            assert uid == 1

        params = {
            'endpoint': self.endpoint,
            'data': {'login': 'John', 'password': 'top-secret'},
            'json': True
        }
        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 400


class TestLoginHandler(object):
    endpoint = 'auth.login'

    @asyncio.coroutine
    def prepare_user(self, application, user):
        now = datetime.now()

        with (yield from application.engine) as conn:
            uid = yield from conn.scalar(users_table.insert().values(
                login=user['login'],
                password=encrypt_password(user['password']),
                created_on=now
            ))
        return uid

    @pytest.mark.handlers
    @pytest.mark.parametrize('params', [
        {'json': False},
        {'json': True}
    ])
    @async_test(attach_server=True)
    def test_success(self, application, db, params, **kwargs):
        server = kwargs.get('server')
        user = {'login': 'John', 'password': 'top-secret'}

        uid = yield from self.prepare_user(application, user)
        assert uid == 1

        params.update(endpoint=self.endpoint, data=user)
        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 200
            assert 'X-ACCESS-TOKEN' in response.headers

    @pytest.mark.handlers
    @pytest.mark.parametrize('params', [
        {'data': {'login': 'John', 'password': 'wrong-password'}},
        {'data': {'login': 'John'}}
    ])
    @async_test(attach_server=True)
    def test_fail(self, application, db, params, **kwargs):
        server = kwargs.get('server')
        user = {'login': 'John', 'password': 'top-secret'}

        uid = yield from self.prepare_user(application, user)
        assert uid == 1

        params.update(endpoint=self.endpoint, json=True)
        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 400

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_missing_user(self, application, db, **kwargs):
        server = kwargs.get('server')
        user = {'login': 'John', 'password': 'top-secret'}

        uid = yield from self.prepare_user(application, user)
        assert uid == 1

        user['login'] = 'Patrick'
        params = {'endpoint': self.endpoint, 'data': user, 'json': True}
        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 404
