from wallet.domain.commands import RegisterAccount, RemoveAccount
from wallet.domain.entities import Account
from wallet.domain.specifications import UniqueAccountNameSpecification
from wallet.domain.storage import Storage


class RegisterAccountHandler:
    __slots__ = ('_storage', )

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def handle(self, cmd: RegisterAccount) -> None:
        account = Account(0, cmd.name, cmd.user)

        async with self._storage as store:
            spec = UniqueAccountNameSpecification(repo=store.accounts)

            satisfied = await spec.is_satisfied_by(account)
            if satisfied:
                await store.accounts.add(account)
                await store.commit()


class RemoveAccountHandler:
    __slots__ = ('_storage', )

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def handle(self, cmd: RemoveAccount) -> None:
        async with self._storage as store:
            await store.accounts.remove(cmd.account)
            await store.commit()
