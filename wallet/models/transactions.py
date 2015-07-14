from marshmallow import Schema, fields
import sqlalchemy
from sqlalchemy.dialects.postgresql import JSON

from .base import create_table


transactions_table = create_table('transactions', (
    sqlalchemy.Column('account_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('accounts.id'), nullable=False),
    sqlalchemy.Column('category_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('categories.id'), nullable=False),
    sqlalchemy.Column('description', sqlalchemy.String(255)),
    sqlalchemy.Column('amount', sqlalchemy.Numeric(), nullable=False),
    sqlalchemy.Column('details', JSON),
    sqlalchemy.Column('created_on', sqlalchemy.DateTime(), nullable=False)
))


transactions_schema = {
    'id': {
        'type': 'integer'
    },
    'account_id': {
        'type': 'integer',
        'coerce': int,
        'required': True,
        'empty': False
    },
    'category_id': {
        'type': 'integer',
        'coerce': int,
        'required': True,
        'empty': False
    },
    'description': {
        'type': 'string',
        'maxlength': 255,
        'empty': True
    },
    'amount': {
        'type': 'number',
        'coerce': float,
        'required': True,
        'empty': False,
    },
    'details': {
        'type': 'list',
        'empty': True,
        'schema': {
            'type': 'dict',
            'schema': {
                'name': {'type': 'string', 'maxlength': 255},
                'price_per_unit': {'type': 'number', 'coerce': float},
                'count': {'type': 'number', 'coerce': float},
                'total': {'type': 'number', 'coerce': float},
            }
        }
    },
    'created_on': {
        'type': 'datetime'
    }
}


class TransactionSerializer(Schema):
    id = fields.Integer()
    account_id = fields.Integer()
    category_id = fields.Integer()
    description = fields.String()
    amount = fields.Float()
    created_on = fields.DateTime(format='%d-%m-%Y %X')
