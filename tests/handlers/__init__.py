import asyncio
from datetime import datetime


class BaseHandlerTest(object):

    @asyncio.coroutine
    def create_instance(self, app, table, raw):
        """
        :param app: Application instance
        :param table: Table instance
        :param raw: Raw instance
        :return: created instance id
        """
        with (yield from app.engine) as conn:
            query = table.insert().values(**raw)
            uid = yield from conn.scalar(query)
        return uid