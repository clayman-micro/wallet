from datetime import datetime
from decimal import Decimal
from typing import Callable, Dict

import sqlalchemy
from aiopg.sa import SAConnection
from cerberus import Validator, errors
from psycopg2 import ProgrammingError, IntegrityError

from .. import exceptions


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
    quant = ''.join(('0.', ''.join(map(lambda x: '0',
                                       range(precision - 1))), '1'))

    def wrapped(value: str) -> Decimal:
        try:
            value = float(value)
            return Decimal(value).quantize(Decimal(quant))
        except ValueError:
            return None
    return wrapped


class CustomValidator(Validator):

    def _validate_type_decimal(self, field, value):
        if not isinstance(value, Decimal):
            self._error(field, errors.ERROR_BAD_TYPE.format('Decimal'))


def validate(payload: Dict, schema: Dict) -> Dict:
    validator = CustomValidator(schema=schema)
    if not validator.validate(payload):
        raise exceptions.ValidationError(validator.errors)
    return validator.document


def serialize(value, exclude=None):
    if exclude and isinstance(exclude, (list, tuple, set)):
        result = {key: value for key, value in iter(value.items())
                  if key not in exclude}
    else:
        result = {key: value for key, value in iter(value.items())}
    return result


async def create_instance(document: Dict, table: sqlalchemy.Table, conn) -> Dict:
    try:
        instance_id = await conn.scalar(sqlalchemy.insert(table, document))
    except ProgrammingError as exc:
        raise exceptions.DatabaseError({'integrity_error': {
            'primary': exc.diag.message_primary,
            'detail': exc.diag.message_detail
        }})
    except IntegrityError as exc:
        raise exceptions.DatabaseError({'integrity_error': {
            'primary': exc.diag.message_primary,
            'detail': exc.diag.message_detail
        }})
    else:
        return {'id': instance_id, **document}


async def get_instance(query, conn: SAConnection):
    result = await conn.execute(query)
    if result.returns_rows:
        if result.rowcount == 1:
            row = await result.fetchone()
            return dict(zip(row.keys(), row.values()))
        elif result.rowcount > 1:
            raise exceptions.MultipleResourcesFound
    raise exceptions.ResourceNotFound


async def update_instance(instance, table: sqlalchemy.Table, conn: SAConnection):
    try:
        result = await conn.execute(
            table.update().returning(*table.c).where(
                table.c.id == instance.get('id')).values(**instance)
        )
        row = await result.fetchone()
    except IntegrityError as exc:
        raise exceptions.DatabaseError({'integrity_error': {
            'primary': exc.diag.message_primary,
            'detail': exc.diag.message_detail
        }})
    except ProgrammingError:
        raise exceptions.DatabaseError
    else:
        return dict(zip(row.keys(), row.values()))


async def remove_instance(instance: Dict, table: sqlalchemy.Table, conn):
    try:
        result = await conn.execute(table.delete().where(
            table.c.id == instance.get('id')))
    except IntegrityError as exc:
        raise exceptions.DatabaseError({'integrity_error': {
            'primary': exc.diag.message_primary,
            'detail': exc.diag.message_detail
        }})
    except ProgrammingError as exc:
        raise exceptions.DatabaseError({'integrity_error': {
            'primary': exc.diag.message_primary,
            'detail': exc.diag.message_detail
        }})
    else:
        return bool(result.rowcount)
