from datetime import datetime
from decimal import Decimal
from typing import Callable, Dict

import cerberus


class ValidationError(Exception):
    def __init__(self, errors):
        self._errors = errors

    @property
    def errors(self):
        return self._errors


class Validator(cerberus.Validator):
    def _validate_type_decimal(self, field, value):
        if not isinstance(value, Decimal):
            self._error(field, cerberus.errors.ERROR_BAD_TYPE.format('Decimal'))

    def validate_payload(self, payload: Dict, update: bool=False) -> Dict:
        if not self.validate(payload, update=update):
            raise ValidationError(self.errors)

        return self.document


def to_bool(value):
    if isinstance(value, bool):
        return value
    else:
        return str(value).lower() in ['true', '1', 'yes']


def to_datetime(value: str) -> datetime:
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')


def to_decimal(precision: int) -> Callable:
    quant = ''.join(('0.', ''.join(map(lambda x: '0',
                                       range(precision - 1))), '1'))

    def wrapped(value: str) -> Decimal:
        try:
            value = float(value)
            return Decimal(value).quantize(Decimal(quant))
        except ValueError:
            return None
    return wrapped
