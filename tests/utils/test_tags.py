import pytest

from wallet.utils.tags import TagsFilter
from wallet.validation import ValidationError


@pytest.mark.utils
@pytest.mark.parametrize('payload', (
    {'name': None},
    {'name': 'Foo'}
))
def test_accounts_filter(payload):
    filters = TagsFilter.from_dict(payload)
    assert isinstance(filters, TagsFilter)


@pytest.mark.utils
@pytest.mark.parametrize('payload', (
    {'name': ''},
))
def test_accounts_fitler_failed(payload):
    with pytest.raises(ValidationError):
        TagsFilter.from_dict(payload)
