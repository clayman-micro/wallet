import sqlalchemy as alchemy

from .base import create_table, to_decimal


table = create_table('accounts', (
    alchemy.Column('name', alchemy.String(255), nullable=False),
    alchemy.Column('original_amount', alchemy.Numeric(20, 2)),
    alchemy.Column('current_amount', alchemy.Numeric(20, 2)),
    alchemy.Column('owner_id', alchemy.Integer,
                   alchemy.ForeignKey('users.id')),
    alchemy.Column('created_on', alchemy.DateTime(), nullable=False)
))

schema = {
    'id': {
        'type': 'integer',
    },
    'name': {
        'type': 'string',
        'maxlength': 255,
        'required': True,
        'empty': False
    },
    'original_amount': {
        'type': 'decimal',
        'coerce': to_decimal(2),
        'empty': True
    },
    'current_amount': {
        'type': 'decimal',
        'coerce': to_decimal(2),
        'readonly': True,
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


def serialize(value):
    return {
        'id': value['id'],
        'name': value['name'],
        'original_amount': float(value['original_amount']),
        'current_amount': float(value['current_amount'])
    }
