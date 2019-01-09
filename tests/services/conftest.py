from collections import defaultdict
from typing import Any, Dict, Iterable, List, TypeVar

import pytest  # type: ignore

from wallet.domain import Repo
from wallet.domain.entities import Account, Operation, Tag, User
from wallet.domain.storage import AccountQuery, OperationQuery, OperationRepo, Storage, TagQuery


Entity = TypeVar("Entity", Account, Tag)
Query = TypeVar("Query", AccountQuery, TagQuery)


class FakeRepo(Repo[Entity, Query]):
    def __init__(self) -> None:
        self._entities: Dict[int, List[Entity]] = defaultdict(list)

    @property
    def entities(self) -> Dict[int, List[Entity]]:
        return self._entities

    async def find(self, query: Query) -> List[Entity]:
        try:
            if query.key:
                result = list(
                    filter(lambda item: item.key == query.key, self._entities[query.user.key])
                )
            elif query.name is not None:
                result = list(
                    filter(
                        lambda item: item.name.lower() == query.name.lower(),
                        self._entities[query.user.key],
                    )
                )
            else:
                result = self._entities[query.user.key]
        except KeyError:
            result = []

        return result

    async def add(self, instance: Entity) -> int:
        self._entities[instance.user.key].append(instance)
        return instance.key

    async def update(self, instance: Entity, fields: Iterable[str]) -> bool:
        pass

    async def remove(self, instance: Entity) -> bool:
        pass


class FakeOperationRepo(OperationRepo):
    def __init__(self) -> None:
        self._entities: Dict[int, List[Operation]] = defaultdict(list)

    @property
    def entities(self) -> Dict[int, List[Operation]]:
        return self._entities

    async def add(self, instance: Operation) -> int:
        self._entities[instance.account.key].append(instance)
        return instance.key

    async def find(self, query: OperationQuery) -> List[Operation]:
        result: List[Operation] = []
        try:
            if query.key:
                result = list(
                    filter(lambda item: item.key == query.key, self._entities[query.account.key])
                )
        except KeyError:
            pass

        return result


class FakeStorage(Storage):
    def __init__(
        self,
        accounts: Repo[Account, AccountQuery],
        operations: FakeOperationRepo,
        tags: Repo[Tag, TagQuery],
    ) -> None:

        super(FakeStorage, self).__init__(accounts, operations, tags)

        self.was_committed = False
        self.was_rolled_back = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.exc_type = exc_type
        self.exc_val = exc_val
        self.exc_tb = exc_tb

        await self.rollback()

    async def commit(self):
        self.was_committed = True

    async def rollback(self):
        self.was_rolled_back = True


@pytest.fixture(scope="function")
def account(fake: Any, user: User) -> Account:
    return Account(1, fake.credit_card_provider(), user=user)


@pytest.fixture(scope="function")
def tag(fake: Any, user: User) -> Tag:
    return Tag(1, fake.safe_color_name(), user=user)


@pytest.fixture(scope="function")
def accounts_repo():
    return FakeRepo[Account, AccountQuery]()


@pytest.fixture(scope="function")
def operations_repo():
    return FakeOperationRepo()


@pytest.fixture(scope="function")
def tags_repo():
    return FakeRepo[Tag, TagQuery]()


@pytest.fixture(scope="function")
def storage(accounts_repo, operations_repo, tags_repo):
    return FakeStorage(accounts_repo, operations_repo, tags_repo)
