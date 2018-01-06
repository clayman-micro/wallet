import re
from typing import List, Optional

from asyncpg.connection import Connection

from wallet.entities import Account, EntityAlreadyExist, EntityNotFound, Owner


Accounts = List[Account]


class AccountsRepository(object):
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

        self._update_pattern = re.compile(r'UPDATE (?P<count>\d+)')

    def _did_update(self, result):
        match = self._update_pattern.search(result)
        if match:
            try:
                count = int(match.group('count'))
            except ValueError:
                count = 0

        return count > 0

    async def _fetch_by_name(self, owner: Owner, name: str) -> bool:
        pass

    async def fetch(self, owner: Owner, name: Optional[str] = None) -> Accounts:
        accounts = []

        async with self._conn.transaction():
            query = [
                'SELECT id, name, amount, original FROM accounts',
                'WHERE (enabled = True'
            ]

            if name:
                query.append(f"AND name LIKE '{name}%'")

            query.append('AND owner_id = $1) ORDER BY created_on ASC;')

            async for row in self._conn.cursor(' '.join(query), owner.pk):
                account = Account(row['name'], row['amount'], owner,
                                  pk=row['id'], original=row['original'])
                accounts.append(account)

        return accounts

    async def fetch_account(self, owner: Owner, pk: int) -> Account:
        query = '''
            SELECT id, name, amount, original FROM accounts
            WHERE enabled = TRUE AND owner_id = $1 AND id = $2
        '''
        row = await self._conn.fetchrow(query, owner.pk, pk)

        if not row:
            raise EntityNotFound()

        return Account(row['name'], row['amount'], owner, pk=row['id'],
                       original=row['original'])

    async def save(self, account: Account) -> int:
        query = '''
            SELECT COUNT(id) FROM accounts WHERE name = $1 AND owner_id = $2
        '''
        async with self._conn.transaction():
            count = await self._conn.fetchval(query, account.name,
                                              account.owner.pk)
            if count:
                raise EntityAlreadyExist()

            query = '''
                INSERT INTO accounts (
                    name, amount, original, enabled, owner_id, created_on
                )
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            '''

            pk = await self._conn.fetchval(query, account.name, account.amount,
                                           account.original, account.enabled,
                                           account.owner.pk, account.created_on)

        return pk

    async def update(self, account: Account, fields) -> bool:
        allowed = ('name', 'amount', 'original')

        index = 2
        query_parts = []
        args = []
        for field in fields:
            if field in allowed:
                query_parts.append(f'{field} = ${index}')
                args.append(getattr(account, field))
                index += 1

        async with self._conn.transaction():
            if 'name' in fields:
                count = await self._conn.fetchval("""
                    SELECT COUNT(id) FROM accounts
                    WHERE name = $1 AND owner_id = $2 AND id != $3
                """, account.name, account.owner.pk, account.pk)

                if count:
                    raise EntityAlreadyExist()

            if query_parts:
                query = f"""
                    UPDATE accounts SET {", ".join(query_parts)} WHERE id = $1;
                """

                result = await self._conn.execute(query, account.pk, *args)
                return self._did_update(result)
            else:
                return False

    async def remove(self, account: Account) -> bool:
        query = '''
            UPDATE accounts SET enabled = FALSE
            WHERE id = $1 AND owner_id = $2 AND enabled = TRUE
        '''
        async with self._conn.transaction():
            result = await self._conn.execute(query, account.pk,
                                              account.owner.pk)

        return self._did_update(result)
