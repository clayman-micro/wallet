import sqlalchemy

from .base import create_table, to_decimal


table = create_table('transaction_details', (
    sqlalchemy.Column('name', sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column('price_per_unit', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('count', sqlalchemy.Numeric(20, 3)),
    sqlalchemy.Column('total', sqlalchemy.Numeric(20, 2)),
    sqlalchemy.Column('transaction_id', sqlalchemy.Integer(),
                      sqlalchemy.ForeignKey('transactions.id'), nullable=False)
))

schema = {
    'id': {
        'type': 'integer'
    },
    'name': {
        'type': 'string',
        'maxlength': 255,
        'required': True
    },
    'price_per_unit': {
        'type': 'decimal',
        'coerce': to_decimal(2),
        'empty': False
    },
    'count': {
        'type': 'decimal',
        'coerce': to_decimal(3),
        'empty': False,
    },
    'total': {
        'type': 'decimal',
        'coerce': to_decimal(2),
        'required': True,
    },
    'transaction_id': {
        'type': 'integer',
        'coerce': int,
        'required': True
    }
}