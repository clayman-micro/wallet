import asyncio
from datetime import datetime

import pytest

from wallet.models import accounts, auth

from tests.conftest import async_test


class BaseAccountTest(object):

    @asyncio.coroutine
    def create_instance(self, app, table, raw):
        """
        :param app: Application instance
        :param table: Table instance
        :param raw: Raw instance
        :return: created instance id
        """
        now = datetime.now()
        raw.setdefault('created_on', now)

        with (yield from app.engine) as conn:
            query = table.insert().values(**raw)
            uid = yield from conn.scalar(query)

        return uid

    @asyncio.coroutine
    def prepare_owner(self, app):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_instance(app, auth.users_table, owner)
        return owner_id

    @asyncio.coroutine
    def prepare_account(self, app, account):
        owner_id = yield from self.prepare_owner(app)
        raw = dict(**account)
        raw.setdefault('owner_id', owner_id)

        raw['id'] = yield from self.create_instance(
            app, accounts.accounts_table, raw)

        return raw


class TestAccountCollection(BaseAccountTest):

    @pytest.mark.handlers
    @pytest.mark.parametrize('endpoint', (
        'api.get_accounts',
        'api.create_account'
    ))
    def test_endpoints_exists(self, application, endpoint):
        assert endpoint in application.router

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_get_success(self, application, db, **kwargs):
        server = kwargs.get('server')
        endpoint = 'api.get_accounts'

        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'current_amount': None}
        expected = yield from self.prepare_account(application, account)
        del expected['created_on']

        with (yield from server.response_ctx('GET', endpoint)) as resp:
            assert resp.status == 200

            response = yield from resp.json()
            assert 'accounts' in response
            assert [expected, ] == response['accounts']

    @pytest.mark.handlers
    @pytest.mark.parametrize('params', (
        {'json': False},
        {'json': True}
    ))
    @async_test(attach_server=True)
    def test_create_success(self, application, db, params, **kwargs):
        server = kwargs.get('server')
        endpoint = 'api.create_account'

        owner_id = yield from self.prepare_owner(application)
        account = {'name': 'Credit card', 'original_amount': 30000.0,
                   'owner_id': owner_id}
        expected = {'id': 1, 'name': 'Credit card', 'original_amount': 30000.0,
                    'current_amount': 0.0, 'owner_id': owner_id}

        params.update(endpoint=endpoint, data=account)
        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 201

            response = yield from response.json()
            assert 'account' in response
            assert expected == response['account']


class TestAccountResource(BaseAccountTest):
    account = {'name': 'Credit card', 'original_amount': 30000.0,
               'current_amount': 0.0}

    @pytest.mark.handlers
    @pytest.mark.parametrize('endpoint', (
        'api.get_account',
        'api.update_account',
        'api.remove_account'
    ))
    def test_endpoints_exists(self, application, endpoint):
        assert endpoint in application.router

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_get_success(self, application, db, **kwargs):
        server = kwargs.get('server')
        endpoint = 'api.get_account'

        expected = yield from self.prepare_account(application, self.account)
        del expected['created_on']

        params = {
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': expected.get('id')}
        }
        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 200

            data = yield from response.json()
            assert 'account' in data
            assert expected == data['account']

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_update_success(self, application, db, **kwargs):
        server = kwargs.get('server')
        endpoint = 'api.update_account'

        expected = yield from self.prepare_account(application, self.account)
        expected['name'] = 'Debit card'
        del expected['created_on']

        params = {
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': expected.get('id')},
            'data': {'name': 'Debit card'},
            'json': True
        }
        with (yield from server.response_ctx('PUT', **params)) as resp:
            assert resp.status == 200

            response = yield from resp.json()
            assert expected == response['account']

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_remove_success(self, application, db, **kwargs):
        server = kwargs.get('server')
        endpoint = 'api.remove_account'

        expected = yield from self.prepare_account(application, self.account)

        params = {
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': expected.get('id')}
        }
        with (yield from server.response_ctx('DELETE', **params)) as response:
            assert response.status == 200

        with (yield from application.engine) as conn:
            query = accounts.accounts_table.count().where(
                accounts.accounts_table.c.id == expected.get('id'))
            count = yield from conn.scalar(query)
            assert count == 0
