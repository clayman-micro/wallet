from collections import defaultdict
from typing import List

import pytest

from wallet.domain.entities import Account, Operation, Tag
from wallet.domain.storage import (
    AccountQuery, AccountsRepo, OperationQuery, OperationsRepo,
    Storage, TagQuery, TagsRepo
)


class FakeAccountsRepo(AccountsRepo):
    def __init__(self):
        self._entities = defaultdict(list)

    async def add(self, account: Account) -> Account:
        self._entities[account.user.key].append(account)
        return account

    async def find(self, query: AccountQuery) -> List[Account]:
        try:
            if query.key:
                result = list(filter(lambda item: item.key == query.key, self._entities[query.user.key]))
            elif query.name:
                result = list(filter(
                    lambda item: item.name.lower() == query.name.lower(),
                    self._entities[query.user.key]
                ))
            else:
                result = self._entities[query.user.key]
        except KeyError:
            result = []

        return result

    @property
    def entities(self):
        return self._entities


class FakeTagsRepo(TagsRepo):
    def __init__(self):
        self._entities = defaultdict(list)

    async def add(self, tag: Tag) -> Tag:
        self._entities[tag.user.key].append(tag)
        return tag

    async def find(self, query: TagQuery) -> List[Tag]:
        try:
            if query.key:
                result = list(filter(lambda item: item.key == query.key, self._entities[query.user.key]))
            elif query.name:
                result = list(filter(
                    lambda item: item.name.lower() == query.name.lower(),
                    self._entities[query.user.key]
                ))
            else:
                result = self._entities[query.user.key]
        except KeyError:
            result = []

        return result

    @property
    def entities(self):
        return self._entities


class FakeOperationsRepo(OperationsRepo):
    def __init__(self):
        self._entities = defaultdict(list)

    async def add(self, operation: Operation) -> Operation:
        self._entities[operation.account.key].append(operation)
        return operation

    async def find(self, query: OperationQuery) -> List[Operation]:
        try:
            if query.key:
                result = list(filter(lambda item: item.key == query.key, self._entities[query.account.key]))
            else:
                result = self._entities[query.account.key]
        except KeyError:
            result = []

        return result

    @property
    def entities(self):
        return self._entities


class FakeStorage(Storage):
    def __init__(self):
        super(FakeStorage, self).__init__()

        self._accounts = FakeAccountsRepo()
        self._operations = FakeOperationsRepo()
        self._tags = FakeTagsRepo()

        self.was_committed = False
        self.was_rolled_back = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.exc_type = exc_type
        self.exc_val = exc_val
        self.exc_tb = exc_tb

    async def commit(self):
        self.was_committed = True

    async def rollback(self):
        self.was_rolled_back = True

    @property
    def accounts(self):
        return self._accounts

    @property
    def operations(self):
        return self._operations

    @property
    def tags(self):
        return self._tags


@pytest.fixture(scope='function')
def storage():
    return FakeStorage()
