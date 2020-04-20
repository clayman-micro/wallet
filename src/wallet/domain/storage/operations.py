from datetime import date
from typing import Iterable, List, Optional

from wallet.domain import Account, Operation, Tag


class OperationRepo:
    async def find(
        self, account: Account, month: Optional[date] = None
    ) -> List[Operation]:
        raise NotImplementedError

    async def find_by_key(self, account: Account, key: int) -> Operation:
        raise NotImplementedError

    async def add(self, operation: Operation) -> int:
        raise NotImplementedError

    async def update(self, operation: Operation, fields: Iterable[str]) -> bool:
        raise NotImplementedError

    async def remove(self, operation: Operation) -> bool:
        raise NotImplementedError

    async def add_tag(self, operation: Operation, tag: Tag) -> bool:
        raise NotImplementedError

    async def remove_tag(self, operation: Operation, tag: Tag) -> bool:
        raise NotImplementedError
