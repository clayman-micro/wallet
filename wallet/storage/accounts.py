# from datetime import datetime
# from decimal import Decimal
# from itertools import groupby
from typing import Dict, List

from asyncpg.connection import Connection

from wallet.storage import AlreadyExist, Resource, ResourceNotFound, update
from wallet.storage.owner import Owner


class Account(Resource):
    __slots__ = (
        'id', 'name', 'amount', 'original', 'enabled', 'owner_id', 'created_on'
    )

    def __init__(self, name: str, owner: Owner, **optional) -> None:
        self.name = name
        self.amount = optional.get('amount', 0.0)
        self.original = optional.get('original', 0.0)

        super(Account, self).__init__(owner, **optional)

    def serialize(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'original': self.original
        }


class AccountsRepo(object):
    def __init__(self, conn: Connection) -> None:
        self.conn: Connection = conn

    async def fetch_many(self, owner: Owner, **search) -> List[Account]:
        result = []

        async with self.conn.transaction():
            query = [
                'SELECT id, name, amount, original FROM accounts',
                'WHERE (enabled = True'
            ]

            if 'name' in search and search['name']:
                query.append(f"AND name LIKE '{search['name']}%'")

            query.append('AND owner_id = $1) ORDER BY created_on ASC;')

            async for row in self.conn.cursor(' '.join(query), owner.id):
                account = Account(row['name'], owner, amount=row['amount'],
                                  original=row['original'], id=row['id'])
                result.append(account)

        return result

    async def fetch(self, owner: Owner, account_id: int) -> Account:
        query = '''
            SELECT id, name, amount, original FROM accounts
            WHERE enabled = TRUE AND owner_id = $1 AND id = $2
        '''
        row = await self.conn.fetchrow(query, owner.id, account_id)

        if not row:
            raise ResourceNotFound()

        return Account(row['name'], owner, amount=row['amount'],
                       original=row['original'], id=row['id'])

    async def create(self, name: str, owner: Owner, **optional) -> Account:
        account = Account(name, owner, amount=optional.get('amount', 0.0),
                          original=optional.get('original', 0.0))

        async with self.conn.transaction():
            query = '''
            SELECT COUNT(id) FROM accounts WHERE name = $1 AND owner_id = $2
            '''
            count = await self.conn.fetchval(query, account.name, owner.id)
            if count:
                raise AlreadyExist()

            query = '''
                INSERT INTO accounts (
                    name, amount, original, enabled, owner_id, created_on
                )
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            '''

            account.id = await self.conn.fetchval(
                query, account.name, account.amount, account.original,
                account.enabled, account.owner_id, account.created_on
            )

        return account

    @update
    async def rename(self, account: Account, name) -> bool:
        async with self.conn.transaction():
            query = '''
                SELECT COUNT(id) FROM accounts
                WHERE (
                    id != $1 AND owner_id = $2 AND enabled = TRUE and name = $3
                )
            '''
            count = await self.conn.fetchval(query, account.id,
                                             account.owner_id, name)
            if count:
                raise AlreadyExist()

            query = '''
                UPDATE accounts SET name = $1 WHERE id = $2
            '''
            result = await self.conn.execute(query, name, account.id)
        return result

    @update
    async def remove(self, account: Account) -> bool:
        async with self.conn.transaction():
            query = '''
                UPDATE accounts SET enabled = FALSE
                WHERE id = $1 AND owner_id = $2 AND enabled = TRUE
            '''
            result = await self.conn.execute(query, account.id,
                                             account.owner_id)
        return result


