import asyncio
from datetime import datetime

from wallet.models.accounts import accounts_table
from wallet.models.auth import users_table, encrypt_password


class BaseHandlerTest(object):

    @asyncio.coroutine
    def create_instance(self, app, table, raw):
        """
        :param app: Application instance
        :param table: Table instance
        :param raw: Raw instance
        :return: created instance id
        """
        with (yield from app['engine']) as conn:
            query = table.insert().values(**raw)
            uid = yield from conn.scalar(query)
        return uid

    @asyncio.coroutine
    def create_owner(self, app, raw):
        owner_id = yield from self.create_instance(app, users_table, {
            'login': raw['login'],
            'password': encrypt_password(raw['password']),
            'created_on': datetime.now()
        })
        return owner_id

    @asyncio.coroutine
    def create_account(self, app, raw):
        raw.setdefault('created_on', datetime.today())
        account_id = yield from self.create_instance(app, accounts_table, raw)
        return account_id
