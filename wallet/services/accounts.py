from wallet.domain import EntityAlreadyExist
from wallet.domain.entities import Account, User
from wallet.domain.storage import AccountQuery, Storage


class AccountsService:
    __slots__ = ('_storage', )

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def register(self, name: str, user: User) -> Account:
        account = Account(key=0, name=name, user=user)

        async with self._storage as store:
            query = AccountQuery(user=user, name=name)
            existed = await store.accounts.find(query)

            if len(existed) > 0:
                raise EntityAlreadyExist()

            account.key = await store.accounts.add(account)
            await store.commit()

        return account
