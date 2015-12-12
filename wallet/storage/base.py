from datetime import datetime
from decimal import Decimal
from typing import Callable

import sqlalchemy
from cerberus import Validator
from cerberus.errors import ERROR_BAD_TYPE

metadata = sqlalchemy.MetaData()


def create_table(name, columns):
    base_columns = [
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True)
    ]
    base_columns.extend(columns)
    return sqlalchemy.Table(name, metadata, *base_columns)


def to_datetime(value: str) -> datetime:
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')


def to_decimal(precision: int) -> Callable:
    def wrapped(value: str) -> Decimal:
        return Decimal(value).quantize(Decimal('0.01'))
    return wrapped


class CustomValidator(Validator):
    def _validate_type_decimal(self, field, value):
        if not isinstance(value, Decimal):
            self._error(field, ERROR_BAD_TYPE.format('Decimal'))
