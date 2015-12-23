"""Add accounts table

Revision ID: 4c0f217ab48
Revises: 49f4f5bbfa3
Create Date: 2015-07-08 22:55:50.470043

"""

from alembic import op
import sqlalchemy as sa

revision = '4c0f217ab48'
down_revision = '49f4f5bbfa3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('original_amount', sa.Numeric(), nullable=True),
        sa.Column('current_amount', sa.Numeric(), nullable=True),
        sa.Column('created_on', sa.DateTime(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('accounts')
