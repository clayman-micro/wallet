from datetime import date

import pytest

from wallet.core.entities.abc import Period
from wallet.core.entities.operations import OperationFilters
from wallet.web.schemas.operations import OperationsFilterSchema


@pytest.mark.unit
@pytest.mark.parametrize(
    "query,expected",
    (
        ({}, {"limit": 10}),
        ({"limit": 20}, {"limit": 20}),
        ({"offset": 10}, {"limit": 10, "offset": 10}),
        ({"offset": 20, "limit": 20}, {"limit": 20, "offset": 20}),
        ({"account": 1}, {"account_key": 1}),
        ({"category": 1}, {"category_key": 1}),
        ({"category": 1}, {"category_key": 1}),
        (
            {"from": "2021-01-01", "to": "2021-01-10"},
            {"period": Period(beginning=date(2021, 1, 1), ending=date(2021, 1, 10))},
        ),
    ),
)
def test_success(user, query, expected):
    schema = OperationsFilterSchema()
    schema.context["user"] = user

    filters = schema.load(query)

    assert filters == OperationFilters(user=user, **expected)
