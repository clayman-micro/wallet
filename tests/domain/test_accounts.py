from decimal import Decimal
from typing import List

import pendulum  # type: ignore
import pytest  # type: ignore

from wallet.domain import Account, Balance, Operation, OperationType


@pytest.mark.unit
@pytest.fixture(scope="module")
def operations_factory(fake):
    def build(raw) -> List[Operation]:
        operations = []

        for index, item in enumerate(raw, start=1):
            amount, account, operation_type, created_on = item

            start = created_on.start_of("month")
            end = created_on.end_of("month")
            created_on = fake.date_time_between_dates(
                datetime_start=start, datetime_end=end
            )

            operation = Operation(
                index,
                Decimal(amount),
                account,
                type=OperationType(operation_type),
                created_on=created_on,
            )
            operations.append(operation)

        return operations

    return build


@pytest.mark.unit
def test_initial_balance(fake, user):
    account = Account(1, fake.credit_card_provider(), user)

    created = pendulum.today()
    assert account.balance == [
        Balance(
            rest=Decimal("0"),
            expenses=Decimal("0"),
            incomes=Decimal("0"),
            month=created.start_of("month").date(),
        )
    ]


@pytest.mark.unit
def test_skip_balance_initialization(fake, user):
    created = pendulum.yesterday()

    balance = [
        Balance(
            rest=Decimal("1000"),
            expenses=Decimal("100"),
            incomes=Decimal("0"),
            month=created.start_of("month").date(),
        )
    ]

    account = Account(1, fake.credit_card_provider(), user, balance=balance)
    assert account.balance == balance


@pytest.mark.unit
def test_apply_operation_to_current_month(fake, user, operations_factory):
    today = pendulum.today().date()

    account = Account(1, fake.credit_card_provider(), user)
    operations = operations_factory((("632.81", account, "expense", today),))

    account.apply_operation(operations[0])

    assert account.balance == [
        Balance(
            rest=Decimal("-632.81"),
            expenses=Decimal("632.81"),
            month=today.start_of("month"),
        )
    ]


@pytest.mark.unit
def test_apply_operations_two_month_earlier_missing_month(
    fake, user, operations_factory
):
    today = pendulum.today().date()
    month = today.start_of("month")

    account = Account(
        1,
        fake.credit_card_provider(),
        user,
        balance=[
            Balance(
                rest=Decimal("5421.55"),
                expenses=Decimal("4578.45"),
                incomes=Decimal("10000"),
                month=month,
            )
        ],
    )
    operations = operations_factory(
        (("632.81", account, "expense", today.subtract(months=2)),)
    )

    account.apply_operation(operations[0])

    assert account.balance == [
        Balance(
            rest=Decimal("-632.81"),
            expenses=Decimal("632.81"),
            month=month.subtract(months=2),
        ),
        Balance(rest=Decimal("-632.81"), month=month.subtract(months=1)),
        Balance(
            rest=Decimal("4788.74"),
            expenses=Decimal("4578.45"),
            incomes=Decimal("10000"),
            month=month,
        ),
    ]


@pytest.mark.unit
def test_apply_operation_two_month_earlier_existing_month(
    fake, user, operations_factory
):
    today = pendulum.today().date()
    month = today.start_of("month")

    account = Account(
        1,
        fake.credit_card_provider(),
        user,
        balance=[
            Balance(
                rest=Decimal("5421.55"),
                expenses=Decimal("4578.45"),
                incomes=Decimal("10000"),
                month=month.subtract(months=2),
            ),
            Balance(
                rest=Decimal("10247.05"),
                expenses=Decimal("3874.50"),
                incomes=Decimal("8700"),
                month=month.subtract(months=1),
            ),
            Balance(
                rest=Decimal("8393.65"),
                expenses=Decimal("6853.40"),
                incomes=Decimal("5000"),
                month=month,
            ),
        ],
    )
    operations = operations_factory(
        (("632.81", account, "income", today.subtract(months=1)),)
    )

    account.apply_operation(operations[0])

    assert account.balance == [
        Balance(
            rest=Decimal("5421.55"),
            expenses=Decimal("4578.45"),
            incomes=Decimal("10000"),
            month=month.subtract(months=2),
        ),
        Balance(
            rest=Decimal("10879.86"),
            expenses=Decimal("3874.50"),
            incomes=Decimal("9332.81"),
            month=month.subtract(months=1),
        ),
        Balance(
            rest=Decimal("9026.46"),
            expenses=Decimal("6853.40"),
            incomes=Decimal("5000"),
            month=month,
        ),
    ]


@pytest.mark.unit
def test_apply_operation_two_month_in_future(fake, user, operations_factory):
    today = pendulum.today().date()
    month = today.start_of("month")

    account = Account(
        1,
        fake.credit_card_provider(),
        user,
        balance=[
            Balance(
                rest=Decimal("5421.55"),
                expenses=Decimal("4578.45"),
                incomes=Decimal("10000"),
                month=month.subtract(months=2),
            ),
            Balance(
                rest=Decimal("10247.05"),
                expenses=Decimal("3874.50"),
                incomes=Decimal("8700"),
                month=month.subtract(months=1),
            ),
            Balance(
                rest=Decimal("8393.65"),
                expenses=Decimal("6853.40"),
                incomes=Decimal("5000"),
                month=month,
            ),
        ],
    )
    operations = operations_factory(
        (("632.81", account, "income", today.add(months=2)),)
    )

    account.apply_operation(operations[0])

    assert account.balance == [
        Balance(
            rest=Decimal("5421.55"),
            expenses=Decimal("4578.45"),
            incomes=Decimal("10000"),
            month=month.subtract(months=2),
        ),
        Balance(
            rest=Decimal("10247.05"),
            expenses=Decimal("3874.50"),
            incomes=Decimal("8700"),
            month=month.subtract(months=1),
        ),
        Balance(
            rest=Decimal("8393.65"),
            expenses=Decimal("6853.40"),
            incomes=Decimal("5000"),
            month=month,
        ),
        Balance(
            rest=Decimal("8393.65"),
            expenses=Decimal("0"),
            incomes=Decimal("0"),
            month=month.add(months=1),
        ),
        Balance(
            rest=Decimal("9026.46"),
            expenses=Decimal("0.0"),
            incomes=Decimal("632.81"),
            month=month.add(months=2),
        ),
    ]


@pytest.mark.unit
def test_rollback_operation_from_current_month(fake, user, operations_factory):
    created = pendulum.yesterday()

    account = Account(1, fake.credit_card_provider(), user)
    operations = operations_factory((("632.81", account, "expense", created),))

    account.rollback_operation(operations[0])

    assert account.balance == [
        Balance(
            rest=Decimal("632.81"),
            expenses=Decimal("-632.81"),
            incomes=Decimal("0"),
            month=created.start_of("month").date(),
        )
    ]


@pytest.mark.unit
def test_rollback_operation_two_month_earlier(fake, user, operations_factory):
    today = pendulum.today()

    account = Account(
        1,
        fake.credit_card_provider(),
        user,
        balance=[
            Balance(
                rest=Decimal("1867.19"),
                expenses=Decimal("632.81"),
                incomes=Decimal("2500"),
                month=today.subtract(months=3).start_of("month").date(),
            ),
            Balance(
                rest=Decimal("1867.19"),
                expenses=Decimal("0"),
                incomes=Decimal("0"),
                month=today.subtract(months=2).start_of("month").date(),
            ),
            Balance(
                rest=Decimal("1103.91"),
                expenses=Decimal("763.28"),
                incomes=Decimal("28189.31"),
                month=today.subtract(months=1).start_of("month").date(),
            ),
            Balance(
                rest=Decimal("28529.94"),
                expenses=Decimal("763.28"),
                incomes=Decimal("28189.31"),
                month=today.start_of("month").date(),
            ),
        ],
    )
    operations = operations_factory(
        (("28189.31", account, "income", today.subtract(months=1)),)
    )

    account.rollback_operation(operations[0])

    assert account.balance == [
        Balance(
            rest=Decimal("1867.19"),
            expenses=Decimal("632.81"),
            incomes=Decimal("2500"),
            month=today.subtract(months=3).start_of("month").date(),
        ),
        Balance(
            rest=Decimal("1867.19"),
            expenses=Decimal("0"),
            incomes=Decimal("0"),
            month=today.subtract(months=2).start_of("month").date(),
        ),
        Balance(
            rest=Decimal("-27085.40"),
            expenses=Decimal("763.28"),
            incomes=Decimal("0"),
            month=today.subtract(months=1).start_of("month").date(),
        ),
        Balance(
            rest=Decimal("340.63"),
            expenses=Decimal("763.28"),
            incomes=Decimal("28189.31"),
            month=today.start_of("month").date(),
        ),
    ]
