from aiohttp_micro.exceptions import EntityAlreadyExist, EntityNotFound
from passport.domain import User

from wallet.core.entities import Account, Category


class AccountAlreadyExist(EntityAlreadyExist):
    def __init__(self, user: User, account: Account) -> None:
        self._user = user
        self._account = account


class AccountNotFound(EntityNotFound):
    def __init__(self, user: User, name: str) -> None:
        self._user = user
        self._name = name


class CategoryAlreadyExist(EntityAlreadyExist):
    def __init__(self, user: User, category: Category) -> None:
        self._user = user
        self._category = category


class CategoryNotFound(EntityNotFound):
    def __init__(self, user: User, name: str) -> None:
        self._user = user
        self._name = name
