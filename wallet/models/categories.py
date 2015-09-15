from marshmallow import Schema, fields
import sqlalchemy as alchemy

from .base import create_table


categories_table = create_table('categories', (
    alchemy.Column('name', alchemy.String(255), unique=True,
                   nullable=False),
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
    'owner_id': {
        'type': 'integer',
        'coerce': int,
        'readonly': True
    }
}


class CategorySerializer(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    type = fields.String()
    owner_id = fields.Integer()
