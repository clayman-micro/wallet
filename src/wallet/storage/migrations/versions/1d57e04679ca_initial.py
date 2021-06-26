"""Initial

Revision ID: 1d57e04679ca
Create Date: 2021-02-09 17:37:32.584181

"""

import sqlalchemy as sa  # type: ignore
from alembic import op  # type: ignore

revision = "1d57e04679ca"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("user", sa.Integer(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.Column("created_on", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "accounts_name_idx", "accounts", ["name", "user", "enabled"], unique=True,
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("user", sa.Integer(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.Column("created_on", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "categories_name_idx", "categories", ["name", "user", "enabled"], unique=True,
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("user", sa.Integer(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.Column("created_on", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "tags_name_idx", "tags", ["name", "user", "enabled"], unique=True,
    )

    op.create_table(
        "category_tags",
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("category_id", "tag_id"),
    )

    op.create_table(
        "operations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column("type", sa.Enum("income", "expense", name="operationtype"), nullable=False,),
        sa.Column("desc", sa.String(length=500), nullable=True),
        sa.Column("user", sa.Integer(), nullable=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.Column("created_on", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    op.drop_table("operations")
    op.drop_table("category_tags")

    op.execute("DROP TYPE operationtype;")

    op.drop_index("tags_name_idx", table_name="tags")
    op.drop_table("tags")

    op.drop_index("categories_name_idx", table_name="categories")
    op.drop_table("categories")

    op.drop_index("accounts_name_idx", table_name="accounts")
    op.drop_table("accounts")
