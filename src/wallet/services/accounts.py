from wallet.domain import Account
from wallet.domain.storage import EntityAlreadyExist, Storage


class AccountsService:
    __slots__ = ("_storage",)

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def register(self, account: Account) -> None:
        async with self._storage as store:
            existed = await store.accounts.find_by_name(
                account.user, account.name
            )

            if len(existed) > 0:
                raise EntityAlreadyExist()

            account.key = await store.accounts.add(account)
            await store.commit()
