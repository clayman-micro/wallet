from dataclasses import dataclass
from typing import Optional

from passport.domain import User

from wallet.core.entities.abc import EntityWithBalance, Filters, Payload


@dataclass
class Tag(EntityWithBalance):
    name: str
    user: User


@dataclass
class TagPayload(Payload):
    name: str


@dataclass
class TagFilters(Filters):
    name: Optional[str] = None
