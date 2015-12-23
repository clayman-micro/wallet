from datetime import datetime

import pytest

from wallet.storage.base import create_instance
from wallet.storage.users import table, encrypt_password


class TestRegistrationHandler(object):

    @pytest.mark.run_loop
    @pytest.mark.parametrize('params', [{'json': False}, {'json': True}])
    async def test_success(self, client, params):
        params['data'] = {'login': 'John', 'password': 'top-secret'}
        params['endpoint'] = 'auth.registration'

        async with client.request('POST', **params) as response:
            assert response.status == 201

    @pytest.mark.run_loop
    @pytest.mark.parametrize('params', [{'json': False}, {'json': True}])
    async def test_fail_without_password(self, client, params):
        params['data'] = {'login': 'John'}
        params['endpoint'] = 'auth.registration'

        async with client.request('POST', **params) as response:
            assert response.status == 400

    @pytest.mark.run_loop
    @pytest.mark.parametrize('params', [{'json': False}, {'json': True}])
    async def test_fail_if_already_existed(self, app, client, params):
        await create_instance(app['engine'], table, {
            'login': 'John', 'password': 'top-secret',
            'created_on': datetime.now()
        })

        params['data'] = {'login': 'John', 'password': 'weak-secret'}
        params['endpoint'] = 'auth.registration'

        async with client.request('POST', **params) as response:
            assert response.status == 400


class TestLoginHandler(object):
    user = {'login': 'John', 'password': 'top-secret'}

    async def create_user(self, engine):
        return await create_instance(engine, table, {
            'created_on': datetime.now(), 'login': self.user['login'],
            'password': encrypt_password(self.user['password'])
        })

    @pytest.mark.run_loop
    @pytest.mark.parametrize('params', [{'json': False}, {'json': True}])
    async def test_success(self, app, client, params):
        await self.create_user(app['engine'])

        params.update(data=self.user, endpoint='auth.login')
        async with client.request('POST', **params) as response:
            assert response.status == 200
            assert 'X-ACCESS-TOKEN' in response.headers

    @pytest.mark.run_loop
    @pytest.mark.parametrize('params', [
        {'data': {'login': 'John', 'password': 'incorrect'}, 'json': True},
        {'data': {'login': 'John'}, 'json': True}
    ])
    async def test_fail(self, app, client, params):
        await self.create_user(app['engine'])

        params['endpoint'] = 'auth.login'
        async with client.request('POST', **params) as response:
            assert response.status == 400

    @pytest.mark.run_loop
    @pytest.mark.parametrize('params', [{'json': False}, {'json': True}])
    async def test_missing_user(self, app, client, params):
        await self.create_user(app['engine'])

        params['data'] = {'login': 'Patrick', 'password': 'weed-secret'}
        params['endpoint'] = 'auth.login'
        async with client.request('POST', **params) as response:
            assert response.status == 404
