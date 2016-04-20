from datetime import datetime

from aiohttp import web

from wallet.storage.base import create_instance
from wallet.storage import accounts, categories, transactions, details, users
from wallet.storage.users import encrypt_password


async def create_owner(owner, app: web.Application):
    async with app['engine'].acquire() as conn:
        return await create_instance({
            'login': owner['login'],
            'password': encrypt_password(owner['password']),
            'created_on': datetime.now()
        }, users.table, conn)


async def create_account(account, app: web.Application):
    account.setdefault('created_on', datetime.today())
    async with app['engine'].acquire() as conn:
        return await create_instance(account, accounts.table, conn)


async def create_category(category, app: web.Application):
    async with app['engine'].acquire() as conn:
        return await create_instance(category, categories.table, conn)


async def create_transaction(transaction, app: web.Application):
    transaction.setdefault('created_on', datetime.now())
    async with app['engine'].acquire() as conn:
        return await create_instance(transaction, transactions.table, conn)

async def create_detail(detail, app: web.Application):
    async with app['engine'].acquire() as conn:
        return await create_instance(detail, details.table, conn)
