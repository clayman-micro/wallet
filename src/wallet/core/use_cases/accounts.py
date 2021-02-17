from logging import Logger
from typing import AsyncGenerator

from passport.domain import User

from wallet.core.entities import Account, AccountFilters, AccountPayload
from wallet.core.services.accounts import AccountService
from wallet.core.storage import Storage


class AccountUseCase:
    def __init__(self, storage: Storage, logger: Logger) -> None:
        self.storage = storage
        self._service: AccountService = AccountService(
            storage=self.storage, logger=logger
        )

    async def get_by_key(self, user: User, key: int) -> Account:
        return self._service.find_by_key(user, key=key)


class AddUseCase(AccountUseCase):
    async def execute(
        self, payload: AccountPayload, dry_run: bool = False
    ) -> Account:
        return await self._service.add(payload=payload, dry_run=dry_run)


class RemoveUseCase(AccountUseCase):
    async def execute(
        self, user: User, key: int, dry_run: bool = False
    ) -> None:
        account = await self.get_by_key(user, key=key)

        await self._service.remove(account, dry_run=dry_run)


class SearchUseCase(AccountUseCase):
    async def execute(
        self, filters: AccountFilters
    ) -> AsyncGenerator[Account, None]:
        async for account in self._service.find(filters=filters):
            yield account
