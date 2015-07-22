"""Add transaction and transaction details tables.

Revision ID: 53820d92432
Revises: 4c0f217ab48
Create Date: 2015-07-18 23:33:16.057119

"""

# revision identifiers, used by Alembic.

from alembic import op
import sqlalchemy as sa

revision = '53820d92432'
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
        sa.Column('created_on', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'transaction_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('price_per_unit', sa.Numeric(), nullable=True),
        sa.Column('count', sa.Numeric(), nullable=True),
        sa.Column('total', sa.Numeric(), nullable=True),
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('transaction_details')
    op.drop_table('transactions')
