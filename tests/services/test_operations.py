import asyncio
from datetime import datetime
from decimal import Decimal
from unittest import mock

import pytest  # type: ignore

from wallet.domain import Operation, OperationType
from wallet.services.operations import OperationsService


class TestOperationsService:
    @pytest.mark.unit
    async def test_add_operation_to_account(self, account, storage):
        now = datetime.now()

        update_account = asyncio.Future()
        update_account.set_result(True)

        storage.accounts.update = mock.MagicMock(return_value=update_account)

        add = asyncio.Future()
        add.set_result(1)

        storage.operations.add = mock.MagicMock(return_value=add)

        operation = Operation(
            key=0,
            amount=Decimal("838"),
            account=account,
            type=OperationType.expense,
            created_on=now,
        )

        service = OperationsService(storage)
        await service.add_to_account(account, operation)

        assert operation == Operation(
            key=1,
            amount=Decimal("838"),
            account=account,
            type=OperationType.expense,
            created_on=now,
        )

        storage.operations.add.assert_called()
        storage.accounts.update.assert_called()
        assert storage.was_committed

    @pytest.mark.unit
    async def test_remove_operation_from_account(
        self, account, operation, storage
    ):
        update_account = asyncio.Future()
        update_account.set_result(True)

        storage.accounts.update = mock.MagicMock(return_value=update_account)

        remove = asyncio.Future()
        remove.set_result(True)

        storage.operations.remove = mock.MagicMock(return_value=remove)

        service = OperationsService(storage)
        await service.remove_from_account(account, operation)

        storage.operations.remove.assert_called()
        storage.accounts.update.assert_called()
        assert storage.was_committed

    @pytest.mark.unit
    async def test_fetch_operations(self, account, operation, tag, storage):
        operation.tags = [tag]

        find_by_operations = asyncio.Future()
        find_by_operations.set_result({operation.key: [tag]})

        storage.tags.find_by_operations = mock.MagicMock(
            return_value=find_by_operations
        )

        find = asyncio.Future()
        find.set_result([operation])

        storage.operations.find = mock.MagicMock(return_value=find)

        service = OperationsService(storage)
        result = await service.fetch(account)

        assert len(result) == 1
        assert result[0] == operation

    @pytest.mark.unit
    async def test_fetch_operation(self, account, operation, tag, storage):
        operation.tags = [tag]

        find_by_operations = asyncio.Future()
        find_by_operations.set_result({operation.key: [tag]})

        storage.tags.find_by_operations = mock.MagicMock(
            return_value=find_by_operations
        )

        find = asyncio.Future()
        find.set_result(operation)

        storage.operations.find_by_key = mock.MagicMock(return_value=find)

        service = OperationsService(storage)
        result = await service.fetch_by_key(account, key=operation.key)

        assert result == operation
