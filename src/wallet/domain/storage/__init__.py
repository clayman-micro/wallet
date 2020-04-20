from wallet.domain.storage.accounts import AccountsRepo
from wallet.domain.storage.operations import OperationRepo
from wallet.domain.storage.tags import TagsRepo


class EntityAlreadyExist(Exception):
    pass


class EntityNotFound(Exception):
    pass


class Storage:
    __slots__ = ("_accounts", "_operations", "_tags")

    def __init__(
        self, accounts: AccountsRepo, operations: OperationRepo, tags: TagsRepo
    ) -> None:
        self._accounts = accounts
        self._operations = operations
        self._tags = tags

    async def __aenter__(self):
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    async def commit(self):
        raise NotImplementedError

    async def rollback(self):
        raise NotImplementedError

    @property
    def accounts(self) -> AccountsRepo:
        return self._accounts

    @property
    def operations(self) -> OperationRepo:
        return self._operations

    @property
    def tags(self) -> TagsRepo:
        return self._tags
