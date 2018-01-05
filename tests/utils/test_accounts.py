import pytest

from wallet.utils.accounts import AccountsFilter
from wallet.validation import ValidationError


@pytest.mark.utils
@pytest.mark.parametrize('payload', (
    {'name': None},
    {'name': 'Foo'}
))
def test_accounts_filter(payload):
    filters = AccountsFilter.from_dict(payload)
    assert isinstance(filters, AccountsFilter)


@pytest.mark.utils
@pytest.mark.parametrize('payload', (
    {'name': ''},
))
def test_accounts_fitler_failed(payload):
    with pytest.raises(ValidationError):
        AccountsFilter.from_dict(payload)
