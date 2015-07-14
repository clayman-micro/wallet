""" Add transactions table

Revision ID: 42891d5fc1a
Revises: 4c0f217ab48
Create Date: 2015-07-11 17:50:36.102926

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '42891d5fc1a'
down_revision = '4c0f217ab48'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('amount', sa.Numeric(), nullable=False),
        sa.Column('details', postgresql.JSON(), nullable=True),
        sa.Column('created_on', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('transactions')