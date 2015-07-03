"""Add categories table

Revision ID: 49f4f5bbfa3
Revises: 20e3b808b4d
Create Date: 2015-07-01 23:13:26.182532

"""
from alembic import op
import sqlalchemy as sa

revision = '49f4f5bbfa3'
down_revision = '20e3b808b4d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )


def downgrade():
    op.drop_table('categories')