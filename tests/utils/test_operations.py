import pytest

from wallet.utils.operations import OpsFilter
from wallet.validation import ValidationError


@pytest.mark.utils
@pytest.mark.parametrize('payload', (
    {'year': None, 'month': None},
    {'year': '2017', 'month': '01'},
))
def test_operations_filter(payload):
    filters = OpsFilter.from_dict(payload)
    assert isinstance(filters, OpsFilter)


@pytest.mark.utils
@pytest.mark.parametrize('payload', (
    {'year': '2017'},
    {'month': '01'},
    {'year': '', 'month': ''},
    {'year': '2017', 'month': '1'},
    {'year': '17', 'month': '01'},
))
def test_operations_filter_failed(payload):
    with pytest.raises(ValidationError):
        OpsFilter.from_dict(payload)
