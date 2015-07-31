from marshmallow import Schema, fields
import sqlalchemy as alchemy

from .base import create_table


accounts_table = create_table('accounts', (
    alchemy.Column('name', alchemy.String(255), nullable=False),
    alchemy.Column('original_amount', alchemy.Numeric()),
    alchemy.Column('current_amount', alchemy.Numeric()),
    alchemy.Column('created_on', alchemy.DateTime(), nullable=False),
    alchemy.Column('owner_id', alchemy.Integer, alchemy.ForeignKey('users.id'))
))

accounts_schema = {
    'id': {
        'type': 'integer',
    },
    'name': {
        'type': 'string',
        'required': True,
        'empty': False
    },
    'original_amount': {
        'type': 'float',
        'coerce': float,
        'empty': True
    },
    'current_amount': {
        'type': 'float',
        'coerce': float,
        'empty': True
    },
    'created_on': {
        'type': 'datetime',
        'empty': True
    },
    'owner_id': {
        'type': 'integer',
        'coerce': int,
        'readonly': True
    }
}


class AccountSerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    original_amount = fields.Float()
    current_amount = fields.Float()
    created_on = fields.DateTime(format='%d-%m-%Y %X')
    owner_id = fields.Integer()
