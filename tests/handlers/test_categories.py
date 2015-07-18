import asyncio
from datetime import datetime

import pytest

from wallet.models import auth, categories

from tests.conftest import async_test
from . import BaseHandlerTest


class BaseCategoriesTest(BaseHandlerTest):

    @asyncio.coroutine
    def prepare_owner(self, app):
        now = datetime.now()

        owner = {'login': 'John', 'password': 'top_secret',
                 'created_on': datetime.now()}
        owner_id = yield from self.create_instance(app, auth.users_table, owner)
        return owner_id

    @asyncio.coroutine
    def prepare_category(self, app, category):
        owner_id = yield from self.prepare_owner(app)

        raw = dict(**category)
        raw.setdefault('owner_id', owner_id)

        raw['id'] = yield from self.create_instance(
            app, categories.categories_table, raw)

        return raw


class TestCategoriesCollection(BaseCategoriesTest):

    @pytest.mark.handlers
    @pytest.mark.parametrize('endpoint', (
        'api.get_categories',
        'api.create_category'
    ))
    def test_endpoints_exists(self, application, endpoint):
        assert endpoint in application.router

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_get_success(self, application, db, **kwargs):
        server = kwargs.get('server')
        endpoint = 'api.get_categories'

        category = {'name': 'Food', 'type': categories.EXPENSE_CATEGORY}
        expected = yield from self.prepare_category(application, category)

        with (yield from server.response_ctx('GET', endpoint)) as resp:
            assert resp.status == 200

            response = yield from resp.json()
            assert 'categories' in response
            assert [expected, ] == response['categories']

            assert 'meta' in response
            assert response['meta']['total'] == 1

    @pytest.mark.handlers
    @pytest.mark.parametrize('params', (
        {'json': False},
        {'json': True}
    ))
    @async_test(attach_server=True)
    def test_create_success(self, application, db, params, **kwargs):
        server = kwargs.get('server')
        endpoint = 'api.create_category'

        owner_id = yield from self.prepare_owner(application)
        category = {'name': 'Food', 'type': categories.EXPENSE_CATEGORY,
                    'owner_id': owner_id}
        expected = {'id': 1, 'name': 'Food', 'owner_id': owner_id,
                    'type': categories.EXPENSE_CATEGORY}

        params.update(endpoint=endpoint, data=category)

        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 201

            response = yield from response.json()
            assert 'category' in response
            assert expected == response['category']


class TestCategoryResource(BaseCategoriesTest):
    category = {'name': 'Food', 'type': categories.EXPENSE_CATEGORY}

    @pytest.mark.handlers
    @pytest.mark.parametrize('endpoint', (
        'api.get_category',
        'api.update_category',
        'api.remove_category'
    ))
    def test_endpoints_exists(self, application, endpoint):
        assert endpoint in application.router

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_get_success(self, application, db, **kwargs):
        server = kwargs.get('server')
        endpoint = 'api.get_category'

        expected = yield from self.prepare_category(application, self.category)

        params = {
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': expected.get('id')}
        }
        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 200

            data = yield from response.json()
            assert 'category' in data
            assert expected == data['category']

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_update_success(self, application, db, **kwargs):
        server = kwargs.get('server')
        endpoint = 'api.update_category'

        expected = yield from self.prepare_category(application, self.category)
        expected['name'] = 'Others'

        params = {
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': expected.get('id')},
            'data': {'name': 'Others'},
            'json': True
        }
        with (yield from server.response_ctx('PUT', **params)) as resp:
            assert resp.status == 200

            response = yield from resp.json()
            assert expected == response['category']

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_remove_success(self, application, db, **kwargs):
        server = kwargs.get('server')
        endpoint = 'api.remove_category'

        expected = yield from self.prepare_category(application, self.category)

        params = {
            'endpoint': endpoint,
            'endpoint_params': {'instance_id': expected.get('id')}
        }
        with (yield from server.response_ctx('DELETE', **params)) as response:
            assert response.status == 200

        with (yield from application.engine) as conn:
            query = categories.categories_table.count().where(
                categories.categories_table.c.id == expected.get('id'))
            count = yield from conn.scalar(query)
            assert count == 0