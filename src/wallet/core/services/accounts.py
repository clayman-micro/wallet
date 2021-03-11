from typing import AsyncGenerator

from passport.domain import User

from wallet.core.entities import (
    Account,
    AccountFilters,
    AccountPayload,
    OperationFilters,
)
from wallet.core.exceptions import AccountAlreadyExist
from wallet.core.services import Service


class AccountService(Service[Account, AccountFilters, AccountPayload]):
    async def add(
        self, payload: AccountPayload, dry_run: bool = False
    ) -> Account:
        account = Account(name=payload.name, user=payload.user)

        filters = AccountFilters(user=payload.user, name=payload.name)
        exists = await self._storage.accounts.exists(filters)
        if exists:
            raise AccountAlreadyExist(user=payload.user, account=account)

        if not dry_run:
            account.key = await self._storage.accounts.save(account)

        self._logger.info(
            "Add new account",
            user=account.user.key,
            name=account.name,
            dry_run=dry_run,
        )

        return account

    async def remove(self, entity: Account, dry_run: bool = False) -> None:
        filters = OperationFilters(user=entity.user, account=entity)
        has_operations = await self._storage.operations.exists(filters)
        if has_operations:
            raise Exception

        if not dry_run:
            await self._storage.accounts.remove(entity=entity)

        self._logger.info(
            "Remove account",
            user=entity.user.key,
            name=entity.name,
            dry_run=dry_run,
        )

    async def find(
        self, filters: AccountFilters
    ) -> AsyncGenerator[Account, None]:
        async for account in self._storage.accounts.fetch(filters=filters):
            yield account

    async def find_by_key(self, user: User, key: int) -> Account:
        return await self._storage.accounts.fetch_by_key(user, key=key)
