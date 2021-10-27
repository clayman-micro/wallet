from datetime import datetime
from decimal import Decimal
from logging import Logger
from typing import Callable

import pytest
from faker import Faker
from passport.domain import User

from wallet.core.entities import Account, Category, Operation, OperationPayload, OperationType
from wallet.core.services.operations import OperationService
from wallet.core.storage import Storage

StorageBuilder = Callable[[Account, Category], Storage]


@pytest.fixture(scope="function")
def prepare_storage(fake_storage: Storage, fake_coroutine) -> StorageBuilder:
    def builder(account: Account, category: Category) -> Storage:
        fake_storage.accounts.fetch_by_key = fake_coroutine(account)
        fake_storage.categories.fetch_by_key = fake_coroutine(category)
        fake_storage.operations.save = fake_coroutine(1)

        return fake_storage

    return builder


PayloadBuilder = Callable[[Account, Category, datetime], OperationPayload]


@pytest.fixture(scope="function")
def payload_builder(user: User):
    def builder(account: Account, category: Category, created_on: datetime) -> OperationPayload:
        return OperationPayload(
            user=user,
            amount=Decimal("199.90"),
            account=account.key,
            category=category.key,
            operation_type=OperationType.expense,
            created_on=created_on,
        )

    return builder


@pytest.mark.unit
async def test_success(
    faker: Faker,
    prepare_storage: StorageBuilder,
    logger: Logger,
    payload_builder: PayloadBuilder,
    user: User,
    account: Account,
    category: Category,
) -> None:
    created_on = faker.date_time_between()
    service = OperationService(prepare_storage(account, category), logger)

    operation = await service.add(payload=payload_builder(account, category, created_on))

    expected = Operation(
        amount=Decimal("199.90"),
        description="",
        user=user,
        account=account,
        category=category,
        operation_type=OperationType.expense,
    )
    expected.key = 1
    expected.created_on = created_on

    assert operation == expected
