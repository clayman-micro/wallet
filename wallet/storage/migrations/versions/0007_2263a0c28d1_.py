"""Add table to store account balance

Revision ID: 2263a0c28d1
Revises: 32211192354
Create Date: 2016-02-27 20:44:05.508988

"""
from alembic import op
import sqlalchemy as sa

revision = '2263a0c28d1'
down_revision = '32211192354'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'balance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=True),
        sa.Column('income', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('expense', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('remain', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'],
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('accounts', 'current_amount')


def downgrade():
    op.add_column('accounts', sa.Column('current_amount',
                                        sa.NUMERIC(precision=20, scale=2),
                                        autoincrement=False, nullable=True))
    op.drop_table('balance')