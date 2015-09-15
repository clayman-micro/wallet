import pytest

from wallet.models import categories

from tests.conftest import async_test
from . import BaseHandlerTest


class TestCategoriesCollection(BaseHandlerTest):

    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    @async_test(create_database=True)
    def test_get_unauthorized(self, application, headers, server):
        params = {
            'headers': headers,
            'url': server.reverse_url('api.get_categories')
        }
        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 401

    @async_test(create_database=True)
    def test_get_success(self, application, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)
        token = yield from server.get_auth_token(owner)

        category = {'name': 'Food', 'owner_id': owner_id}
        category_id = yield from self.create_instance(
            application, categories.categories_table, category)

        params = {
            'headers': {'X-ACCESS-TOKEN': token},
            'url': server.reverse_url('api.get_categories')
        }
        with (yield from server.response_ctx('GET', **params)) as resp:
            assert resp.status == 200

            expected = {'id': category_id, 'name': 'Food',
                        'owner_id': owner_id}

            response = yield from resp.json()
            assert 'categories' in response
            assert [expected, ] == response['categories']

    @async_test(create_database=True)
    def test_get_success_only_for_owner(self, application, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        category = {'name': 'Food', 'owner_id': owner_id}
        yield from self.create_instance(
            application, categories.categories_table, category)

        another_owner = {'login': 'Paul', 'password': 'top_secret'}
        yield from self.create_owner(application, another_owner)
        token = yield from server.get_auth_token(another_owner)

        params = {
            'headers': {'X-ACCESS-TOKEN': token},
            'url': server.reverse_url('api.get_categories')
        }

        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 200

            data = yield from response.json()
            assert 'categories' in data
            assert data['categories'] == []

    @pytest.mark.parametrize('headers', ({}, {'X-ACCESS-TOKEN': 'fake-token'}))
    @async_test(create_database=True)
    def test_create_unauthorized(self, application, headers, server):
        owner = {'login': 'Paul', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        category = {'name': 'Food', 'owner_id': owner_id}

        params = {
            'data': category,
            'headers': headers,
            'url': server.reverse_url('api.create_category')
        }
        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 401

    @pytest.mark.parametrize('params', ({'json': False}, {'json': True}))
    @async_test(create_database=True)
    def test_create_success(self, application, params, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)
        token = yield from server.get_auth_token(owner)

        params['headers'] = {'X-ACCESS-TOKEN': token}
        params['data'] = {'name': 'Food'}
        params['url'] = server.reverse_url('api.create_category')

        with (yield from server.response_ctx('POST', **params)) as response:
            assert response.status == 201

            expected = {'id': 1, 'name': 'Food', 'owner_id': owner_id}

            response = yield from response.json()
            assert 'category' in response
            assert expected == response['category']


class TestCategoryResource(BaseHandlerTest):

    @pytest.mark.parametrize('method,endpoint,headers', (
        ('GET', 'api.get_category', {}),
        ('GET', 'api.get_category', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('PUT', 'api.update_category', {}),
        ('PUT', 'api.update_category', {'X-ACCESS-TOKEN': 'fake-token'}),
        ('DELETE', 'api.remove_category', {}),
        ('DELETE', 'api.remove_category', {'X-ACCESS-TOKEN': 'fake-token'})
    ))
    @async_test(create_database=True)
    def test_unauthorized(self, application, method, endpoint, headers,server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        category = {'name': 'Food', 'owner_id': owner_id}
        category_id = yield from self.create_instance(
            application, categories.categories_table, category)

        params = {
            'headers': headers,
            'url': server.reverse_url(endpoint, {'instance_id': category_id})
        }
        with (yield from server.response_ctx(method, **params)) as response:
            assert response.status == 401

    @pytest.mark.parametrize('method,endpoint', (
            ('GET', 'api.get_account'),
            ('PUT', 'api.update_account'),
            ('DELETE', 'api.remove_account'),
    ))
    @async_test(create_database=True)
    def test_does_not_belong(self, application, method, endpoint, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        category = {'name': 'Food', 'owner_id': owner_id}
        category_id = yield from self.create_instance(
            application, categories.categories_table, category)

        another_owner = {'login': 'Sam', 'password': 'top_secret'}
        yield from self.create_owner(application, another_owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (
                    yield from server.get_auth_token(another_owner))
            },
            'url': server.reverse_url(endpoint,
                                      {'instance_id': category_id})
        }
        with (yield from server.response_ctx(method, **params)) as response:
            assert response.status == 404

    @pytest.mark.parametrize('method,endpoint', (
            ('GET', 'api.get_account'),
            ('PUT', 'api.update_account'),
            ('DELETE', 'api.remove_account')
    ))
    @async_test(create_database=True)
    def test_missing(self, application, method, endpoint, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        yield from self.create_owner(application, owner)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url(endpoint, {'instance_id': 1})
        }
        with (yield from server.response_ctx(method, **params)) as response:
            assert response.status == 404

    @async_test(create_database=True)
    def test_get_success(self, application, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        category = {'name': 'Food', 'owner_id': owner_id}
        category_id = yield from self.create_instance(
            application, categories.categories_table, category)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.get_category',
                                      {'instance_id': category_id})
        }
        with (yield from server.response_ctx('GET', **params)) as response:
            assert response.status == 200

            expected = {'id': 1, 'name': 'Food', 'owner_id': owner_id}

            data = yield from response.json()
            assert 'category' in data
            assert expected == data['category']

    @pytest.mark.handlers
    @async_test(create_database=True)
    def test_update_success(self, application, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        category = {'name': 'Food', 'owner_id': owner_id}
        category_id = yield from self.create_instance(
            application, categories.categories_table, category)

        params = {
            'data': {'name': 'Car'},
            'json': True,
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.update_category',
                                      {'instance_id': category_id})
        }

        with (yield from server.response_ctx('PUT', **params)) as resp:
            assert resp.status == 200

            expected = {'id': 1, 'name': 'Car', 'owner_id': owner_id}

            response = yield from resp.json()
            assert expected == response['category']

    @async_test(create_database=True)
    def test_remove_success(self, application, server):
        owner = {'login': 'John', 'password': 'top_secret'}
        owner_id = yield from self.create_owner(application, owner)

        category = {'name': 'Food', 'owner_id': owner_id}
        category_id = yield from self.create_instance(
            application, categories.categories_table, category)

        params = {
            'headers': {
                'X-ACCESS-TOKEN': (yield from server.get_auth_token(owner))
            },
            'url': server.reverse_url('api.remove_category',
                                      {'instance_id': category_id})
        }
        with (yield from server.response_ctx('DELETE', **params)) as response:
            assert response.status == 200

        with (yield from application.engine) as conn:
            query = categories.categories_table.count().where(
                categories.categories_table.c.id == category_id)
            count = yield from conn.scalar(query)
            assert count == 0
