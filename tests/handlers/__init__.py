from datetime import datetime

from aiohttp import web

from wallet.storage.base import create_instance
from wallet.storage.accounts import table as accounts_table
from wallet.storage.categories import table as categories_table
from wallet.storage.transactions import table as transactions_table
from wallet.storage.details import table as details_table
from wallet.storage.users import table as users_table, encrypt_password


async def create_owner(app: web.Application, owner):
    return await create_instance(app['engine'], users_table, {
        'login': owner['login'],
        'password': encrypt_password(owner['password']),
        'created_on': datetime.now()
    })


async def create_account(app: web.Application, account):
    account.setdefault('current_amount', account.get('original_amount'))
    account.setdefault('created_on', datetime.today())
    return await create_instance(app['engine'], accounts_table, account)


async def create_category(app: web.Application, category):
    return await create_instance(app['engine'], categories_table, category)


async def create_transaction(app: web.Application, transaction):
    transaction.setdefault('created_on', datetime.now())
    return await create_instance(app['engine'], transactions_table, transaction)

async def create_detail(app: web.Application, detail):
    return await create_instance(app['engine'], details_table, detail)
