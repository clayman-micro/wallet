from typing import Dict, Union

from wallet.validation import ValidationError, Validator


schema = {
    'name': {'type': 'string', 'empty': True, 'minlength': 2}
}


class TagsFilter(object):
    __slots__ = ('_name', )

    def __init__(self, name: str=None) -> None:
        self._name = name

    @property
    def name(self):
        return self._name

    @classmethod
    def from_dict(cls, filters: Dict[str, Union[int, str]]) -> 'TagsFilter':
        validator = Validator(schema=schema)

        for field in ('name', ):
            if field in filters and filters[field] is None:
                del filters[field]

        is_valid = validator.validate(filters)
        if not is_valid:
            raise ValidationError(validator.errors)

        return TagsFilter(validator.document)

    def to_dict(self):
        result = {}

        if self._name:
            result['name'] = self._name

        return result
