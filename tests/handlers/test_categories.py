import asyncio
from datetime import datetime

import pytest

from wallet.models import categories

from tests.conftest import async_test


class BaseCategoriesTest(object):

    @asyncio.coroutine
    def prepare_category(self, application, category):
        now = datetime.now()

        category.setdefault('type', categories.EXPENSE_CATEGORY)
        with (yield from application.engine) as conn:
            query = categories.categories_table.insert().values(
                name=category.get('name'), type=category.get('type'))
            uid = yield from conn.scalar(query)

        return uid


class TestGetCategoriesCollection(BaseCategoriesTest):
    endpoint = 'api.get_categories'

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_success(self, application, db, **kwargs):
        server = kwargs.get('server')
        category = {'name': 'Food'}
        expected = {'id': 1, 'name': 'Food',
                    'type': categories.EXPENSE_CATEGORY}

        uid = yield from self.prepare_category(application, category)
        assert uid == 1

        with (yield from server.response_ctx('GET', self.endpoint)) as resp:
            assert resp.status == 200

            response = yield from resp.json()
            assert 'categories' in response
            assert [expected, ] == response['categories']

            assert 'meta' in response
            assert response['meta']['total'] == 1


class TestGetCategoryResource(BaseCategoriesTest):
    endpoint = 'api.get_category'

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_success(self, application, db, **kwargs):
        server = kwargs.get('server')
        category = {'name': 'Food'}
        expected = {'id': 1, 'name': 'Food',
                    'type': categories.EXPENSE_CATEGORY}

        uid = yield from self.prepare_category(application, category)
        assert uid == 1

        params = {
            'endpoint': self.endpoint,
            'endpoint_params': {'instance_id': uid}
        }
        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 200

            data = yield from response.json()
            assert 'category' in data
            assert expected == data['category']


class TestCreateCategoryResource(BaseCategoriesTest):
    endpoint = 'api.create_category'

    @pytest.mark.handlers
    @pytest.mark.parametrize('params', [
        {'json': False},
        {'json': True}
    ])
    @async_test(attach_server=True)
    def test_success(self, application, db, params, **kwargs):
        server = kwargs.get('server')
        category = {'name': 'Food', 'type': categories.EXPENSE_CATEGORY}
        expected = {'id': 1, 'name': 'Food',
                    'type': categories.EXPENSE_CATEGORY}

        params.update(endpoint=self.endpoint, data=category)
        with (yield from server.response_ctx('POST', **params)) as resp:
            assert resp.status == 201

            response = yield from resp.json()
            assert 'category' in response
            assert expected == response['category']


class TestUpdateCategoryResource(BaseCategoriesTest):
    endpoint = 'api.update_category'

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_success_with_json(self, application, db, **kwargs):
        server = kwargs.get('server')
        category = {'name': 'Food', 'type': categories.EXPENSE_CATEGORY}
        expected = {'id': 1, 'name': 'Gym',
                    'type': categories.EXPENSE_CATEGORY}

        uid = yield from self.prepare_category(application, category)
        assert uid == 1

        params = {
            'endpoint': self.endpoint,
            'endpoint_params': {'instance_id': uid},
            'data': {'name': 'Gym'},
            'json': True
        }
        with (yield from server.response_ctx('PUT', **params)) as resp:
            print(resp.text)
            assert resp.status == 200

            response = yield from resp.json()
            assert expected == response['category']

        application.engine.close()


class TestRemoveCategoryResource(BaseCategoriesTest):
    endpoint = 'api.remove_category'

    @pytest.mark.handlers
    @async_test(attach_server=True)
    def test_success(self, application, db, **kwargs):
        server = kwargs.get('server')
        category = {'name': 'Food', 'type': categories.EXPENSE_CATEGORY}

        uid = yield from self.prepare_category(application, category)
        assert uid == 1

        params = {
            'endpoint': self.endpoint,
            'endpoint_params': {'instance_id': uid}
        }
        with (yield from server.response_ctx('DELETE', **params)) as response:
            assert response.status == 200

        with (yield from application.engine) as conn:
            query = categories.categories_table.count().where(
                categories.categories_table.c.id == uid)
            count = yield from conn.scalar(query)
            assert count == 0
