from typing import Dict, Union

from wallet.validation import Validator


schema = {
    'year': {
        'type': 'string',  'maxlength': 4, 'minlength': 4,
        'dependencies': 'month', 'empty': True
    },
    'month': {
        'type': 'string', 'maxlength': 2, 'minlength': 2,
        'dependencies': 'year', 'empty': True
    }
}


class OpsFilter(object):
    __slots__ = ('_year', '_month')

    def __init__(self, year: str=None, month: str=None) -> None:
        self._year = year
        self._month = month

    @property
    def year(self):
        return self._year

    @property
    def month(self):
        return self._month

    @classmethod
    def from_dict(cls, filters: Dict[str, Union[int, str]]) -> 'OpsFilter':
        validator = Validator(schema=schema)

        for field in ('month', 'year'):
            if field in filters and filters[field] is None:
                del filters[field]

        document = validator.validate_payload(filters)
        return OpsFilter(**document)

    def to_dict(self):
        result = {}

        if self._year and self._month:
            result['year'] = self._year
            result['month'] = self._month

        return result
