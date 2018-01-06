from typing import Dict

from wallet.entities import Account, Operation, Owner
from wallet.interactors import accounts, operations


class OperationsAPIAdapter(object):
    def __init__(self, accounts_repo, operations_repo) -> None:
        self._accounts_repo = accounts_repo
        self._operations_repo = operations_repo

    def serialize(self, operation: Operation) -> Dict:
        return {
            'id': operation.pk,
            'type': operation.type.value,
            'amount': operation.amount,
            'description': operation.description,
            'created_on': operation.created_on.strftime('%Y-%m-%dT%H:%M:%S')
        }

    async def fetch_account(self, owner: Owner, account_pk: int) -> Account:
        interactor = accounts.GetAccountInteractor(self._accounts_repo)
        interactor.set_params(owner, account_pk)

        account = await interactor.execute()

        return account

    async def fetch(self, owner: Owner, account_pk: int, filters=None):
        account = await self.fetch_account(owner, account_pk)

        interactor = operations.GetOperationsInteractor(self._operations_repo)
        interactor.set_params(account, filters)
        items = await interactor.execute()

        result = {
            'operations': [self.serialize(item) for item in items],
            'meta': {
                'total': len(items)
            }
        }

        if filters:
            result['meta']['filters'] = filters.to_dict()

        return result

    async def add_operation(self, owner: Owner, account_pk: int, payload):
        account = await self.fetch_account(owner, account_pk)

        interactor = operations.CreateOperationInteractor(
            self._accounts_repo, self._operations_repo
        )
        interactor.set_params(account, payload)

        operation = await interactor.execute()

        return {'operation': self.serialize(operation)}

    async def fetch_operation(self, owner: Owner, account_pk: int,
                              operation_pk: int) -> Dict:
        account = await self.fetch_account(owner, account_pk)

        interactor = operations.GetOperationInteractor(self._operations_repo)
        interactor.set_params(account, operation_pk)
        operation = await interactor.execute()

        return {'operation': self.serialize(operation)}

    async def update_operation(self, owner: Owner, account_pk: int,
                               operation_pk: int, payload: Dict) -> Dict:
        account = await self.fetch_account(owner, account_pk)

        interactor = operations.UpdateOperationInteractor(
            self._accounts_repo, self._operations_repo
        )
        interactor.set_params(account, operation_pk, payload)

        operation = await interactor.execute()

        return {'operation': self.serialize(operation)}

    async def remove_operation(self, owner: Owner, account_pk: int,
                               operation_pk: int) -> None:
        account = await self.fetch_account(owner, account_pk)

        interactor = operations.RemoveOperationInteractor(
            self._accounts_repo, self._operations_repo
        )
        interactor.set_params(account, operation_pk)

        await interactor.execute()
