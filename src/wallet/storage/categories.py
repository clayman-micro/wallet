from datetime import datetime

import sqlalchemy  # type: ignore
from aiohttp_storage.storage import metadata  # type: ignore


categories = sqlalchemy.Table(
    "categories",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("user", sqlalchemy.Integer),
    sqlalchemy.Column("enabled", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column(
        "created_on", sqlalchemy.DateTime, default=datetime.utcnow
    ),
)


category_tags = sqlalchemy.Table(
    "category_tags",
    metadata,
    sqlalchemy.Column(
        "category_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
    sqlalchemy.Column(
        "tag_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
)
