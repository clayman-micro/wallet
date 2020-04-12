from typing import Iterable, List

from wallet.domain import Account, User


class AccountNotFound(Exception):
    pass


class AccountsRepo:
    async def find(self, user: User) -> List[Account]:
        raise NotImplementedError

    async def find_by_key(self, user: User, key: int) -> Account:
        raise NotImplementedError

    async def find_by_name(self, user: User, name: str) -> List[Account]:
        raise NotImplementedError

    async def add(self, operation: Account) -> int:
        raise NotImplementedError

    async def update(self, operation: Account, fields: Iterable[str]) -> bool:
        raise NotImplementedError

    async def remove(self, operation: Account) -> bool:
        raise NotImplementedError
