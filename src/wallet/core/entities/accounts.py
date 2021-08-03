from dataclasses import dataclass
from typing import AsyncGenerator, Optional

from passport.domain import User

from wallet.core.entities.abc import EntityWithBalance, Filters, Payload


@dataclass
class Account(EntityWithBalance):
    name: str
    user: User


AccountStream = AsyncGenerator[Account, None]


@dataclass
class AccountFilters(Filters):
    name: Optional[str] = None


@dataclass
class AccountPayload(Payload):
    name: str
