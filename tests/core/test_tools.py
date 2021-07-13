import pytest


from wallet.core.tools import month_range


@pytest.fixture
def current_month_test_case(today, month):
    return {"start": today, "expected": [month]}


@pytest.fixture
def two_months_in_past_test_case(today, month):
    return {
        "start": today.subtract(months=2),
        "expected": [month.subtract(months=2), month.subtract(months=1), month],
    }


@pytest.fixture
def several_months_in_future_test_case(today, month):
    return {
        "start": today.subtract(months=2),
        "to": today.add(months=2),
        "expected": [
            month.subtract(months=2),
            month.subtract(months=1),
            month,
            month.add(months=1),
            month.add(months=2),
        ],
    }


@pytest.fixture(
    params=["current_month_test_case", "two_months_in_past_test_case", "several_months_in_future_test_case"]
)
def month_ranges(request):
    return request.getfixturevalue(request.param)


@pytest.mark.unit
def test_month_range(month_ranges):
    assert list(month_range(start=month_ranges.get("start"), to=month_ranges.get("to", None))) == month_ranges.get(
        "expected", []
    )


@pytest.mark.unit
def test_wrong_month_range(today):
    start = today.add(months=1)
    to = today.subtract(months=1)

    with pytest.raises(ValueError):
        list(month_range(start=start, to=to))
