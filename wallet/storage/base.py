from datetime import datetime
from decimal import Decimal
from typing import Callable, Dict

import sqlalchemy
from cerberus import Validator
from cerberus.errors import ERROR_BAD_TYPE
from psycopg2 import ProgrammingError, IntegrityError

from ..exceptions import DatabaseError, ValidationError
from ..utils.db import Connection


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
        try:
            value = float(value)
            return Decimal(value).quantize(Decimal('0.01'))
        except ValueError:
            return None
    return wrapped


class CustomValidator(Validator):

    def _validate_type_decimal(self, field, value):
        if not isinstance(value, Decimal):
            self._error(field, ERROR_BAD_TYPE.format('Decimal'))


def validate(payload: Dict, schema: Dict) -> Dict:
    validator = CustomValidator(schema=schema)
    if not validator.validate(payload):
        raise ValidationError(validator.errors)
    return validator.document


def serialize(value):
    return {key: value for key, value in iter(value.items())}


async def create_instance(engine, table: sqlalchemy.Table, instance: Dict):
    query = table.insert().values(**instance)

    instance_id = None
    async with Connection(engine) as conn:
        try:
            instance_id = await conn.scalar(query)
        except ProgrammingError as exc:
            raise DatabaseError
        except IntegrityError as exc:
            raise DatabaseError({'integrity_error': {
                'primary': exc.diag.message_primary,
                'detail': exc.diag.message_detail
            }})

    return instance_id


async def get_instance(engine, query):
    instance = None

    async with Connection(engine) as conn:
        result = await conn.execute(query)
        if result.returns_rows and result.rowcount == 1:
            row = await result.fetchone()
            instance = dict(zip(row.keys(), row.values()))

    return instance


async def update_instance(engine, table: sqlalchemy.Table, instance):
    query = table.update().where(
        table.c.id == instance.get('id')).values(**instance)

    async with Connection(engine) as conn:
        try:
            result = await conn.execute(query)
        except IntegrityError as exc:
            raise DatabaseError({'integrity_error': {
                'primary': exc.diag.message_primary,
                'detail': exc.diag.message_detail
            }})
        except ProgrammingError as exc:
            raise

    return bool(result.rowcount)


async def remove_instance(engine, table: sqlalchemy.Table, instance: Dict):
    query = table.delete().where(table.c.id == instance.get('id'))

    async with Connection(engine) as conn:
        try:
            result = await conn.execute(query)
        except IntegrityError as exc:
            raise DatabaseError({'integrity_error': {
                'primary': exc.diag.message_primary,
                'detail': exc.diag.message_detail
            }})
        except ProgrammingError as exc:
            raise

    return bool(result.rowcount)
