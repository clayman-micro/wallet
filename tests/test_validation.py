from datetime import datetime

import pytest

from wallet.validation import Validator


@pytest.mark.parametrize('payload', ('True', 'true', '1', 'yes'))
def test_validator_coerce_boolean(payload):
    schema = {'enabled': {'type': 'boolean', 'coerce': 'bool'}}

    validator = Validator(schema)
    document = validator.validate_payload({'enabled': payload})

    assert isinstance(document['enabled'], bool)
    assert document['enabled']


def test_validator_coerce_datetime():
    schema = {'created_on': {'type': 'datetime', 'coerce': 'datetime'}}

    validator = Validator(schema)
    document = validator.validate_payload({'created_on': '2017-12-01T23:23:23'})

    assert isinstance(document['created_on'], datetime)


@pytest.mark.parametrize('payload', ({}, {'foo': 'bar'}))
def test_validator_utcnow_default_setter(payload):
    validator = Validator({'created_on': {
        'type': 'datetime',
        'coerce': 'datetime',
        'default_setter': 'utcnow',
    }})
    document = validator.validate_payload(payload, update=True)

    print(document)
    assert 'created_on' in document
    assert isinstance(document['created_on'], datetime)
