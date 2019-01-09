from datetime import date
from typing import Optional

from wallet.domain import Query, Repo, UnitOfWork
from wallet.domain.entities import Account, Operation, Tag, User


class AccountQuery(Query):
    __slots__ = ("user", "key", "name")

    def __init__(self, user: User, name: str = "", key: int = 0) -> None:

        super(AccountQuery, self).__init__(key)

        self.user = user
        self.name = name


class TagQuery(Query):
    __slots__ = ("user", "key", "name", "operation")

    def __init__(self, user: User, name: str = "", key: int = 0, operation: Optional[Operation] = None) -> None:

        super(TagQuery, self).__init__(key)

        self.user = user
        self.name = name
        self.operation = operation


class OperationQuery(Query):
    __slots__ = ("account", "key", "month")

    def __init__(self, account: Account, key: int = 0, month: Optional[date] = None) -> None:

        super(OperationQuery, self).__init__(key)

        self.account = account
        self.month = month


class OperationRepo(Repo[Operation, OperationQuery]):
    async def add_tag(self, instance: Operation, tag: Tag) -> bool:
        raise NotImplementedError

    async def remove_tag(self, instance: Operation, tag: Tag) -> bool:
        raise NotImplementedError


class Storage(UnitOfWork):
    __slots__ = ("_accounts", "_operations", "_tags")

    def __init__(self, accounts: Repo[Account, AccountQuery], operations: OperationRepo,
                 tags: Repo[Tag, TagQuery]) -> None:
        self._accounts = accounts
        self._operations = operations
        self._tags = tags

    @property
    def accounts(self) -> Repo:
        return self._accounts

    @property
    def operations(self) -> OperationRepo:
        return self._operations

    @property
    def tags(self) -> Repo:
        return self._tags
