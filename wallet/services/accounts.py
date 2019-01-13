from wallet.domain import Account, User
from wallet.domain.storage import EntityAlreadyExist, Storage
from wallet.validation import Validator


class AccountValidator(Validator):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("schema", {
            "name": {"required": True, "empty": False, "type": "string"}
        })

        super(AccountValidator, self).__init__(*args, **kwargs)


class AccountsService:
    __slots__ = ("_storage",)

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def register(self, name: str, user: User) -> Account:
        account = Account(key=0, name=name, user=user)

        async with self._storage as store:
            existed = await store.accounts.find_by_name(user, name)

            if len(existed) > 0:
                raise EntityAlreadyExist()

            account.key = await store.accounts.add(account)
            await store.commit()

        return account