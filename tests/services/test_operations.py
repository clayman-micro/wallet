import asyncio
from datetime import datetime
from decimal import Decimal
from unittest import mock

import pytest  # type: ignore

from wallet.domain import Operation, OperationType
from wallet.services.operations import OperationsService, OperationValidator
from wallet.validation import ValidationError


class TestOperationValidator:
    @pytest.mark.unit
    def test_valid_payload(self, fake):
        created_on = fake.past_datetime(start_date="-30d")

        validator = OperationValidator()
        result = validator.validate_payload({
            "amount": "169.0",
            "type": "expense",
            "description": "Apple Music",
            "created_on": created_on.strftime("%Y-%m-%dT%H:%M:%S")
        })

        assert result == {
            "amount": Decimal('169.00'),
            "type": OperationType.expense,
            "description": "Apple Music",
            "created_on": created_on
        }

    @pytest.mark.unit
    @pytest.mark.parametrize('payload', (
        {},
        {"amount": "foo"},
        {"amount": "169.0", "type": ""},
        {"amount": "169.0", "type": "foo"},
        {"amount": "169.0", "created": "foo"},
        {"amount": "169.0", "created": "2019-01-01"},
    ))
    def test_invalid_payload(self, payload):
        with pytest.raises(ValidationError):
            validator = OperationValidator()
            validator.validate_payload(payload)


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

        service = OperationsService(storage)
        operation = await service.add_to_account(account, Decimal("838"), created_on=now)

        assert operation == Operation(
            1, Decimal("838"), account, type=OperationType.expense, created_on=now
        )

        storage.operations.add.assert_called()
        storage.accounts.update.assert_called()
        assert storage.was_committed

    @pytest.mark.unit
    async def test_remove_operation_from_account(self, account, operation, storage):
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

        storage.tags.find_by_operations = mock.MagicMock(return_value=find_by_operations)

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

        storage.tags.find_by_operations = mock.MagicMock(return_value=find_by_operations)

        find = asyncio.Future()
        find.set_result(operation)

        storage.operations.find_by_key = mock.MagicMock(return_value=find)

        service = OperationsService(storage)
        result = await service.fetch_by_key(account, key=operation.key)

        assert result == operation
