import asyncio
from datetime import datetime
import json

from aiohttp import request
import pytest

from wallet.models.auth import users_table, encrypt_password

from tests.conftest import create_server, async_test


class TestRegistrationHandler(object):

    @pytest.mark.handlers
    @async_test
    def test_success_with_json(self, application, db):
        srv, domain = yield from create_server(application)

        payload = json.dumps({'login': 'John', 'password': 'top-secret'})
        url = ''.join((domain, application.router['auth.registration'].url()))
        headers = {'content-type': 'application/json'}

        resp = yield from request('POST', url, headers=headers,
                                  loop=application.loop, data=payload)
        assert resp.status == 201
        resp.close()

    @pytest.mark.handlers
    @async_test
    def test_success_with_plain(self, application, db):
        srv, domain = yield from create_server(application)

        payload = {'login': 'John', 'password': 'top-secret'}
        url = ''.join((domain, application.router['auth.registration'].url()))

        resp = yield from request('POST', url, data=payload,
                                  loop=application.loop)

        assert resp.status == 201
        resp.close()

    @pytest.mark.handlers
    @async_test
    def test_registration_without_password(self, application, db):
        srv, domain = yield from create_server(application)

        payload = json.dumps({'login': 'John'})
        url = ''.join((domain, application.router['auth.registration'].url()))
        headers = {'content-type': 'application/json'}

        resp = yield from request('POST', url, headers=headers,
                                  loop=application.loop, data=payload)
        assert resp.status == 400
        resp.close()

    @pytest.mark.handlers
    @async_test
    def test_registration_with_already_existed(self, application, db):
        with (yield from application.engine) as conn:
            uid = yield from conn.scalar(users_table.insert().values(
                login='John', password='top-secret',
                created_on=datetime.now()))

            assert uid == 1

        srv, domain = yield from create_server(application)

        payload = json.dumps({'login': 'John', 'password': 'top-secret'})
        url = ''.join((domain, application.router['auth.registration'].url()))
        headers = {'content-type': 'application/json'}

        resp = yield from request('POST', url, headers=headers,
                                  loop=application.loop, data=payload)
        assert resp.status == 400
        resp.close()


class TestLoginHandler(object):

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
    @async_test
    def test_success_with_json(self, application, db):
        user = {'login': 'John', 'password': 'top-secret'}

        uid = yield from self.prepare_user(application, user)
        assert uid == 1

        srv, domain = yield from create_server(application)

        payload = json.dumps(user)
        url = ''.join((domain, application.router['auth.login'].url()))
        headers = {'content-type': 'application/json'}

        resp = yield from request('POST', url, headers=headers,
                                  loop=application.loop, data=payload)

        assert resp.status == 200
        assert 'X-ACCESS-TOKEN' in resp.headers
        resp.close()

    @pytest.mark.handlers
    @async_test
    def test_success_with_plane(self, application, db):
        user = {'login': 'John', 'password': 'top-secret'}

        uid = yield from self.prepare_user(application, user)
        assert uid == 1

        srv, domain = yield from create_server(application)

        url = ''.join((domain, application.router['auth.login'].url()))

        resp = yield from request('POST', url, data=user,
                                  loop=application.loop)

        assert resp.status == 200
        assert 'X-ACCESS-TOKEN' in resp.headers
        resp.close()

    @pytest.mark.handlers
    @async_test
    def test_wrong_credentials(self, application, db):
        user = {'login': 'John', 'password': 'top-secret'}

        uid = yield from self.prepare_user(application, user)
        assert uid == 1

        srv, domain = yield from create_server(application)

        user['password'] = 'wrong-password'
        payload = json.dumps(user)
        url = ''.join((domain, application.router['auth.login'].url()))
        headers = {'content-type': 'application/json'}

        resp = yield from request('POST', url, headers=headers,
                                  loop=application.loop, data=payload)

        assert resp.status == 400

    @pytest.mark.handlers
    @async_test
    def test_without_password(self, application, db):
        user = {'login': 'John', 'password': 'top-secret'}

        uid = yield from self.prepare_user(application, user)
        assert uid == 1

        srv, domain = yield from create_server(application)

        del user['password']
        payload = json.dumps(user)
        url = ''.join((domain, application.router['auth.login'].url()))
        headers = {'content-type': 'application/json'}

        resp = yield from request('POST', url, headers=headers,
                                  loop=application.loop, data=payload)

        assert resp.status == 400

    @pytest.mark.handlers
    @async_test
    def test_missing_user(self, application, db):
        user = {'login': 'John', 'password': 'top-secret'}

        uid = yield from self.prepare_user(application, user)
        assert uid == 1

        srv, domain = yield from create_server(application)

        user['login'] = 'Patrick'
        payload = json.dumps(user)
        url = ''.join((domain, application.router['auth.login'].url()))
        headers = {'content-type': 'application/json'}

        resp = yield from request('POST', url, headers=headers,
                                  loop=application.loop, data=payload)

        assert resp.status == 404