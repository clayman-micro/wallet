from marshmallow import Schema, fields
import sqlalchemy as alchemy

from .base import create_table


categories_table = create_table('categories', (
    alchemy.Column('name', alchemy.String(255), unique=True,
                   nullable=False),
    alchemy.Column('type', alchemy.String(20), nullable=False),
    alchemy.Column('owner_id', alchemy.Integer, alchemy.ForeignKey('users.id'))
))

INCOME_CATEGORY = 'income'
EXPENSE_CATEGORY = 'expense'
CATEGORY_TYPES = (INCOME_CATEGORY, EXPENSE_CATEGORY)


categories_schema = {
    'id': {
        'type': 'integer'
    },
    'name': {
        'type': 'string',
        'maxlength': 255,
        'required': True,
        'empty': False
    },
    'type': {
        'type': 'string',
        'maxlength': 20,
        'required': True,
        'empty': False,
        'allowed': CATEGORY_TYPES
    },
    'owner_id': {
        'type': 'integer',
        'nullable': True
    }
}


class CategorySerializer(Schema):
    id = fields.Integer()
    name = fields.String()
    type = fields.String()
    owner_id = fields.Integer()
