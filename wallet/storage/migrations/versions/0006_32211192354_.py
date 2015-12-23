"""Alter money field to Numeric with fixed precision

Revision ID: 32211192354
Revises: 47878bd6052
Create Date: 2015-12-12 13:02:42.555983

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '32211192354'
down_revision = '47878bd6052'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('accounts', 'original_amount', type_=sa.Numeric(20, 2))
    op.alter_column('accounts', 'current_amount', type_=sa.Numeric(20, 2))

    op.alter_column('transactions', 'amount', type_=sa.Numeric(20, 2))

    op.alter_column('transaction_details', 'price_per_unit',
                    type_=sa.Numeric(20, 2))
    op.alter_column('transaction_details', 'count', type_=sa.Numeric(20, 3))
    op.alter_column('transaction_details', 'total', type_=sa.Numeric(20, 2))


def downgrade():
    op.alter_column('accounts', 'original_amount', type_=sa.Numeric())
    op.alter_column('accounts', 'current_amount', type_=sa.Numeric())

    op.alter_column('transactions', 'amount', type_=sa.Numeric())

    op.alter_column('transaction_details', 'price_per_unit',
                    type_=sa.Numeric())
    op.alter_column('transaction_details', 'count', type_=sa.Numeric())
    op.alter_column('transaction_details', 'total', type_=sa.Numeric())
