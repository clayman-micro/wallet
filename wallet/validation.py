from datetime import datetime
from decimal import Decimal
from typing import Callable, Dict, Optional

import cerberus  # type: ignore


class ValidationError(Exception):
    def __init__(self, errors):
        self._errors = errors

    @property
    def errors(self):
        return self._errors


def to_decimal(precision: int) -> Callable:
    quant = ''.join(('0.', ''.join(map(lambda x: '0',
                                       range(precision - 1))), '1'))

    def wrapped(value: str) -> Optional[Decimal]:
        try:
            v = float(value)
            return Decimal(v).quantize(Decimal(quant))
        except ValueError:
            return None
    return wrapped


class Validator(cerberus.Validator):
    def __init__(self, *args, precision: int = 2, **kwargs) -> None:
        super(Validator, self).__init__(*args, **kwargs)
        self.precision = precision

    def _validate_type_decimal(self, value):
        return isinstance(value, Decimal)

    def _normalize_coerce_bool(self, value):
        if isinstance(value, bool):
            return value
        else:
            return str(value).lower() in ['true', '1', 'yes']

    def _normalize_coerce_datetime(self, value):
        if value:
            if isinstance(value, datetime):
                return value
            else:
                return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')

    def _normalize_coerce_decimal(self, value):
        return to_decimal(self.precision)(value)

    def _normalize_default_setter_utcnow(self, document):
        return datetime.utcnow()

    def validate_payload(self, payload: Dict, update: bool = False) -> Dict:
        self.allow_unknown = update
        if not self.validate(payload, update=update):
            raise ValidationError(self.errors)

        return self.document
