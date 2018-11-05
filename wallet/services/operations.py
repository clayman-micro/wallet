from datetime import datetime

from wallet.domain.commands import AddOperationToAccount
from wallet.domain.entities import Operation
from wallet.domain.storage import Storage


class AddOperationToAccountHandler:
    __slots__ = ('_storage', )

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def handle(self, cmd: AddOperationToAccount) -> None:
        account = cmd.account

        description = cmd.description
        if not description:
            description = ''

        created_on = cmd.created_on
        if not cmd.created_on:
            created_on = datetime.now()

        operation = Operation(cmd.amount, account, type=cmd.type,
                              description=description, created_on=created_on)

        async with self._storage as store:
            await store.operations.add(operation)
            await store.commit()
