"""Add users table

Revision ID: 20e3b808b4d
Revises:
Create Date: 2015-06-29 21:14:31.670401

"""

from alembic import op
import sqlalchemy as sa


revision = '20e3b808b4d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('login', sa.String(length=255), nullable=False),
        sa.Column('password', sa.String(length=130), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_on', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('login')
    )


def downgrade():
    op.drop_table('users')
