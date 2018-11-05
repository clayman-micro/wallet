from datetime import date
from typing import List, Optional

from wallet.domain import Query, Repository, UnitOfWork
from wallet.domain.entities import Account, Operation, Tag, User


class AccountQuery(Query):
    __slots__ = ('user', 'key', 'name')

    def __init__(self, user: User, name: Optional[str] = None, key: Optional[int] = 0) -> None:
        super(AccountQuery, self).__init__(key)

        self.user = user
        self.name = name


class AccountsRepo(Repository):
    async def find(self, query: AccountQuery) -> List[Account]:
        raise NotImplementedError

    async def add(self, account: Account) -> int:
        raise NotImplementedError


class TagQuery(Query):
    __slots__ = ('user', 'key', 'name')

    def __init__(self, user: User, name: Optional[str] = None, key: Optional[int] = 0) -> None:
        super(TagQuery, self).__init__(key)

        self.user = user
        self.name = name


class TagsRepo(Repository):
    async def find(self, query: TagQuery) -> List[Tag]:
        raise NotImplementedError

    async def add(self, tag: Tag) -> int:
        raise NotImplementedError


class OperationQuery(Query):
    __slots__ = ('account', 'key', 'month')

    def __init__(self, account: Account, key: Optional[int] = 0, month: Optional[date] = None) -> None:
        super(OperationQuery, self).__init__(key)

        self.account = account
        self.month = month


class OperationsRepo(Repository):
    async def find(self, query: Query) -> List[Tag]:
        raise NotImplementedError

    async def add(self, operation: Operation) -> int:
        pass


class Storage(UnitOfWork):
    __slots__ = ('_accounts', '_operations', '_tags')

    def __init__(self):
        self._accounts = AccountsRepo()
        self._operations = OperationsRepo()
        self._tags = TagsRepo()

    @property
    def accounts(self):
        return self._accounts

    @property
    def operations(self):
        return self._operations

    @property
    def tags(self):
        return self._tags
