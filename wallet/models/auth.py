from passlib.handlers.pbkdf2 import pbkdf2_sha512

import sqlalchemy as alchemy

from .base import create_table


users_table = create_table('users', (
    alchemy.Column('login', alchemy.String(255), unique=True,
                   nullable=False),
    alchemy.Column('password', alchemy.String(130),
                   nullable=False),
    alchemy.Column('last_login', alchemy.DateTime),
    alchemy.Column('created_on', alchemy.DateTime)
))

users_schema = {
    'id': {
        'type': 'integer'
    },
    'login': {
        'type': 'string',
        'required': True,
        'empty': False
    },
    'password': {
        'type': 'string',
        'required': True,
        'empty': False
    },
    'last_login': {
        'type': 'datetime'
    },
    'created_on': {
        'type': 'datetime'
    }
}


def encrypt_password(password):
    return pbkdf2_sha512.encrypt(password, rounds=10000, salt_size=10)


def verify_password(password, encrypted_password):
    try:
        valid = pbkdf2_sha512.verify(password, encrypted_password)
    except ValueError:
        valid = False
    return valid
