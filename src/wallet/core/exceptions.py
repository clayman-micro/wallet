from typing import Dict, Iterable

from aiohttp_micro.core.exceptions import EntityAlreadyExist, EntityNotFound
from passport.domain import User

from wallet.core.entities import Account, Category, OperationPayload


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


class CategoriesNotFound(EntityNotFound):
    def __init__(self, user: User, keys: Iterable[int]) -> None:
        self._user = user
        self._keys = keys


class OperationNotFound(EntityNotFound):
    pass


class UnprocessableOperations(Exception):
    def __init__(self, user: User, operations: Iterable[OperationPayload]) -> None:
        self._user = user
        self._operations = operations


class ValidationError(Exception):
    def __init__(self, errors: Dict[str, str]) -> None:
        self._errors = errors

    @property
    def errors(self) -> Dict[str, str]:
        return self.errors
