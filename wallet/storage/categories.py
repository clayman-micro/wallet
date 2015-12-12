import sqlalchemy

from .base import create_table


table = create_table('categories', (
    sqlalchemy.Column('name', sqlalchemy.String(255), unique=True,
                      nullable=False),
    sqlalchemy.Column('owner_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id'))
))

schema = {
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
