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
        'required': True,
    },
    'count': {
        'type': 'decimal',
        'coerce': to_decimal(3),
        'required': True,
    },
    'total': {
        'type': 'decimal',
        'coerce': to_decimal(2),
    },
    'transaction_id': {
        'type': 'integer',
        'coerce': int
    }
}


def serialize(value):
    return {
        'id': value['id'],
        'name': value['name'],
        'price_per_unit': round(float(value['price_per_unit']), 2),
        'count': round(float(value['count']), 3),
        'total': round(float(value['total']), 2),
        'transaction_id': value['transaction_id']
    }
