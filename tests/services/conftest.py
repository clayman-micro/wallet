from decimal import Decimal
from typing import Any

import pytest  # type: ignore

from wallet.domain import Account, Operation, Tag, User
from wallet.domain.storage import AccountsRepo, OperationRepo, Storage, TagsRepo


class FakeStorage(Storage):
    def __init__(
        self, accounts: AccountsRepo, operations: OperationRepo, tags: TagsRepo
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
def operation(fake, today, account):
    return Operation(
        key=1,
        amount=Decimal("838.00"),
        account=account,
        description="Fuel",
        created_on=today,
    )


@pytest.fixture(scope="function")
def tag(fake: Any, user: User) -> Tag:
    return Tag(1, fake.safe_color_name(), user=user)


@pytest.fixture(scope="function")
def accounts_repo():
    return AccountsRepo()


@pytest.fixture(scope="function")
def operations_repo():
    return OperationRepo()


@pytest.fixture(scope="function")
def tags_repo():
    return TagsRepo


@pytest.fixture(scope="function")
def storage(accounts_repo, operations_repo, tags_repo):
    return FakeStorage(accounts_repo, operations_repo, tags_repo)
