from datetime import datetime

import sqlalchemy  # type: ignore
from aiohttp_storage.storage import metadata  # type: ignore

from wallet.core.entities import OperationType


operations = sqlalchemy.Table(
    "operations",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("amount", sqlalchemy.Numeric(20, 2), nullable=False),
    sqlalchemy.Column("type", sqlalchemy.Enum(OperationType), nullable=False),
    sqlalchemy.Column("desc", sqlalchemy.String(500)),
    sqlalchemy.Column("user", sqlalchemy.Integer),
    sqlalchemy.Column(
        "account_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sqlalchemy.Column(
        "category_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("categories.id", ondelete="CASCADE"),
    ),
    sqlalchemy.Column("enabled", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column(
        "created_on", sqlalchemy.DateTime, default=datetime.utcnow
    ),
)
