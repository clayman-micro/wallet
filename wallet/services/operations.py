from datetime import datetime

from wallet.domain.commands import AddOperationToAccount
from wallet.domain.entities import Account, Operation
from wallet.domain.storage import Storage


class AddOperationToAccountHandler:
    __slots__ = ('_storage', )

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def handle(self, cmd: AddOperationToAccount) -> None:
        account: Account = cmd.account

        description = cmd.description
        if not description:
            description = ''

        created_on = datetime.now()
        if cmd.created_on:
            created_on = cmd.created_on

        async with self._storage as store:
            operation = Operation(
                key=0,
                amount=cmd.amount,
                account=account,
                description=description,
                type=cmd.type,
                created_on=created_on
            )
            operation.key = await store.operations.add(operation)

            account.apply_operation(operation)

            await store.accounts.update(account, balance=account.balance)
            await store.commit()
