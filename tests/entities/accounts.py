from decimal import Decimal
from typing import List

import pendulum
import pytest

from wallet.entities.accounts import Account, Balance
from wallet.entities.operations import Operation, OperationType


@pytest.fixture(scope='module')
def operations_factory(fake):
    def build(raw) -> List[Operation]:
        operations = []

        for index, item in enumerate(raw, start=1):
            amount, operation_type, created_on = item

            start = created_on.start_of('month')
            end = created_on.end_of('month')
            created_on = fake.date_time_between_dates(datetime_start=start,
                                                      datetime_end=end)

            operation = Operation(pk=index, amount=Decimal(amount),
                                  type=OperationType(operation_type),
                                  created_on=created_on)
            operations.append(operation)

        return operations
    return build


def test_initial_balance():
    created = pendulum.yesterday()

    account = Account(pk=1, name='Visa Classic', created_on=created)

    assert account.balance == [
        Balance(rest=Decimal('0'), expenses=Decimal('0'),
                incomes=Decimal('0'), month=created.start_of('month').date())
    ]


def test_skip_balance_initialization(fake):
    created = pendulum.yesterday()

    balance = [
        Balance(rest=Decimal('1000'), expenses=Decimal('100'),
                incomes=Decimal('0'), month=created.start_of('month').date())
    ]

    account = Account(pk=1, name='Visa Classic', balance=balance,
                      created_on=created)
    assert account.balance == balance


def test_calculate_balance_on_init(fake, operations_factory):
    created = pendulum.parse('2018-06-10', exact=True)
    today = pendulum.today().date()

    operations = operations_factory((
        ('632.81', 'expense', created.subtract(months=3)),
        ('2500', 'income', created.subtract(months=3)),
        ('763.28', 'expense', created.subtract(months=1)),
        ('28189.31', 'income', created.subtract(months=1)),
        ('763.28', 'expense', created),
        ('28189.31', 'income', created),
    ))

    account = Account(pk=1, name='Visa Classic', operations=operations,
                      created_on=created)

    balance = [
        Balance(
            rest=Decimal('1867.19'), expenses=Decimal('632.81'),
            incomes=Decimal('2500'),
            month=created.subtract(months=3).start_of('month')
        ),
        Balance(
            rest=Decimal('1867.19'), expenses=Decimal('0'),
            incomes=Decimal('0'),
            month=created.subtract(months=2).start_of('month')
        ),
        Balance(
            rest=Decimal('29293.22'), expenses=Decimal('763.28'),
            incomes=Decimal('28189.31'),
            month=created.subtract(months=1).start_of('month')
        ),
        Balance(
            rest=Decimal('56719.25'), expenses=Decimal('763.28'),
            incomes=Decimal('28189.31'),
            month=created.start_of('month')
        )
    ]

    current = created.start_of('month').add(months=1)
    while current <= today:
        balance.append(Balance(rest=Decimal('56719.25'),
                               month=current.start_of('month')))
        current = current.add(months=1)

    assert account.balance == balance


def test_apply_operation_to_current_month(operations_factory):
    today = pendulum.today().date()

    operations = operations_factory((
        ('632.81', 'expense', today),
    ))

    account = Account(pk=1, name='Visa Classic', created_on=today)
    account.apply_operation(operations[0])

    assert account.balance == [
        Balance(rest=Decimal('-632.81'), expenses=Decimal('632.81'),
                month=today.start_of('month'))
    ]


def test_apply_operations_two_month_earlier_missing_month(operations_factory):
    today = pendulum.today().date()
    month = today.start_of('month')

    operations = operations_factory((
        ('632.81', 'expense', today.subtract(months=2)),
    ))

    account = Account(pk=1, name='Visa Classic', balance=[
        Balance(rest=Decimal('5421.55'), expenses=Decimal('4578.45'),
                incomes=Decimal('10000'), month=month)
    ], created_on=today)
    account.apply_operation(operations[0])

    assert account.balance == [
        Balance(rest=Decimal('-632.81'), expenses=Decimal('632.81'),
                month=month.subtract(months=2)),
        Balance(rest=Decimal('-632.81'), month=month.subtract(months=1)),
        Balance(rest=Decimal('4788.74'), expenses=Decimal('4578.45'),
                incomes=Decimal('10000'), month=month),
    ]


def test_apply_operation_two_month_earlier_existing_month(operations_factory):
    today = pendulum.today().date()
    month = today.start_of('month')

    operations = operations_factory((
        ('632.81', 'income', today.subtract(months=1)),
    ))

    account = Account(pk=1, name='Visa Classic', balance=[
        Balance(rest=Decimal('5421.55'), expenses=Decimal('4578.45'),
                incomes=Decimal('10000'), month=month.subtract(months=2)),
        Balance(rest=Decimal('10247.05'), expenses=Decimal('3874.50'),
                incomes=Decimal('8700'), month=month.subtract(months=1)),
        Balance(rest=Decimal('8393.65'), expenses=Decimal('6853.40'),
                incomes=Decimal('5000'), month=month)
    ], created_on=today)
    account.apply_operation(operations[0])

    assert account.balance == [
        Balance(rest=Decimal('5421.55'), expenses=Decimal('4578.45'),
                incomes=Decimal('10000'), month=month.subtract(months=2)),
        Balance(rest=Decimal('10879.86'), expenses=Decimal('3874.50'),
                incomes=Decimal('9332.81'), month=month.subtract(months=1)),
        Balance(rest=Decimal('9026.46'), expenses=Decimal('6853.40'),
                incomes=Decimal('5000'), month=month)
    ]


def test_rollback_operation_from_current_month(operations_factory):
    created = pendulum.yesterday()

    operations = operations_factory((
        ('632.81', 'expense', created),
    ))

    account = Account(pk=1, name='Visa Classic', operations=operations,
                      created_on=created)
    account.rollback_operation(operations[0])

    assert account.balance == [
        Balance(rest=Decimal('0'), expenses=Decimal('0'), incomes=Decimal('0'),
                month=created.start_of('month').date())
    ]


def test_rollback_operation_two_month_earlier(operations_factory):
    today = pendulum.today()

    operations = operations_factory((
        ('632.81', 'expense', today.subtract(months=3)),
        ('2500', 'income', today.subtract(months=3)),
        ('763.28', 'expense', today.subtract(months=1)),
        ('28189.31', 'income', today.subtract(months=1)),
        ('763.28', 'expense', today),
        ('28189.31', 'income', today),
    ))

    account = Account(pk=1, name='Visa Classic', operations=operations,
                      created_on=today)
    account.rollback_operation(operations[3])

    assert account.balance == [
        Balance(
            rest=Decimal('1867.19'), expenses=Decimal('632.81'),
            incomes=Decimal('2500'),
            month=today.subtract(months=3).start_of('month').date()
        ),
        Balance(
            rest=Decimal('1867.19'), expenses=Decimal('0'),
            incomes=Decimal('0'),
            month=today.subtract(months=2).start_of('month').date()
        ),
        Balance(
            rest=Decimal('1103.91'), expenses=Decimal('763.28'),
            incomes=Decimal('0'),
            month=today.subtract(months=1).start_of('month').date()
        ),
        Balance(
            rest=Decimal('28529.94'), expenses=Decimal('763.28'),
            incomes=Decimal('28189.31'),
            month=today.start_of('month').date()
        )
    ]
