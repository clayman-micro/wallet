"""Move type from category to transaction

Revision ID: 47878bd6052
Revises: 53820d92432
Create Date: 2015-08-27 15:46:32.022434

"""

# revision identifiers, used by Alembic.
revision = '47878bd6052'
down_revision = '53820d92432'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

from wallet.models.transactions import EXPENSE_TRANSACTION


def upgrade():
    op.drop_column('categories', 'type')

    op.add_column('transactions', sa.Column('type', sa.String(length=20),
                                            nullable=False,
                                            server_default=EXPENSE_TRANSACTION))
    op.create_index(op.f('ix_transactions_type'), 'transactions', ['type'],
                    unique=False)


def downgrade():
    op.drop_index(op.f('ix_transactions_type'), table_name='transactions')

    op.drop_column('transactions', 'type')
    op.add_column('categories', sa.Column('type', sa.VARCHAR(length=20),
                                          autoincrement=False, nullable=False,
                                          server_default=EXPENSE_TRANSACTION))
