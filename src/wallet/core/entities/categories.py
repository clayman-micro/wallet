from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from passport.domain import User

from wallet.core.entities.abc import EntityWithBalance, Filters, Payload
from wallet.core.entities.tags import Tag


@dataclass
class Category(EntityWithBalance):
    name: str
    user: User
    tags: List[Tag] = field(default_factory=list)


@dataclass
class CategoryFilters(Filters):
    name: Optional[str] = None
    names: Iterable[str] = field(default_factory=list)


@dataclass
class CategoryPayload(Payload):
    name: str
    tags: List[int] = field(default_factory=list)
