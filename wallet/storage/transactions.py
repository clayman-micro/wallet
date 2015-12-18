from datetime import datetime

import sqlalchemy

from .base import create_table, to_datetime, to_decimal


INCOME_TRANSACTION = 'income'
EXPENSE_TRANSACTION = 'expense'
TRANSFER_TRANSACTION = 'transfer'
TRANSACTION_TYPES = (INCOME_TRANSACTION, EXPENSE_TRANSACTION,
                     TRANSFER_TRANSACTION)

table = create_table('transactions', (
    sqlalchemy.Column('type', sqlalchemy.String(20), nullable=False),
    sqlalchemy.Column('description', sqlalchemy.String(255)),
    sqlalchemy.Column('amount', sqlalchemy.Numeric(20, 2), nullable=False),
    sqlalchemy.Column('account_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('accounts.id'), nullable=False),
    sqlalchemy.Column('category_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('categories.id'), nullable=False),
    sqlalchemy.Column('created_on', sqlalchemy.DateTime(), nullable=False)
))

schema = {
    'id': {
        'type': 'integer'
    },
    'type': {
        'type': 'string',
        'maxlength': 20,
        'required': True,
        'empty': False,
        'allowed': TRANSACTION_TYPES
    },
    'description': {
        'type': 'string',
        'maxlength': 255,
        'empty': True
    },
    'amount': {
        'type': 'decimal',
        'coerce': to_decimal(2),
        'required': True,
        'empty': False
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
    'created_on': {
        'type': 'datetime',
        'coerce': to_datetime,
        'empty': True
    }
}


def serialize(value):
    return {
        'id': value['id'],
        'type': value['type'],
        'description': value['description'],
        'amount': float(value['amount']),
        'account_id': value['account_id'],
        'category_id': value['category_id'],
        'created_on': datetime.strftime(value['created_on'], '%Y-%m-%dT%H:%M:%S')
    }
