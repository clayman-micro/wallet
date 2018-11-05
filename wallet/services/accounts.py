from wallet.domain.commands import RegisterAccount
from wallet.domain.entities import Account
from wallet.domain.specifications import UniqueAccountNameSpecification
from wallet.domain.storage import Storage


class RegisterAccountHandler:
    __slots__ = ('_storage', )

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def handle(self, cmd: RegisterAccount) -> None:
        account = Account(name=cmd.name, user=cmd.user)

        async with self._storage as store:
            spec = UniqueAccountNameSpecification(repo=store.accounts)

            satisfied = await spec.is_satisfied_by(account)
            if satisfied:
                await store.accounts.add(account)
                await store.commit()
