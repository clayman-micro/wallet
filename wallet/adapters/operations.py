from typing import Dict

from wallet.entities import Account, Operation, Owner, Tag
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


class OperationTagsAPIAdapter(object):
    def __init__(self, accounts_repo, operations_repo, tags_repo) -> None:
        self._accounts_repo = accounts_repo
        self._operations_repo = operations_repo
        self._tags_repo = tags_repo

    async def fetch_account(self, owner: Owner, pk: int) -> Account:
        interactor = accounts.GetAccountInteractor(self._accounts_repo)
        interactor.set_params(owner, pk)
        account = await interactor.execute()
        return account

    async def fetch_operation(self, account: Account, pk: int) -> Operation:
        interactor = operations.GetOperationInteractor(self._operations_repo)
        interactor.set_params(account, pk)
        operation = await interactor.execute()
        return operation

    def serialize(self, tag: Tag):
        return {
            'id': tag.pk,
            'name': tag.name
        }

    async def fetch_tags(self, owner: Owner, account_pk, operation_pk):
        account = await self.fetch_account(owner, account_pk)
        operation = await self.fetch_operation(account, operation_pk)

        tags = []
        for tag in await self._operations_repo.fetch_tags(operation):
            tags.append(tag)

        return {'tags': [self.serialize(tag) for tag in tags]}

    async def add_tag(self, owner: Owner, account_pk, operation_pk, payload):
        account = await self.fetch_account(owner, account_pk)
        operation = await self.fetch_operation(account, operation_pk)

        interactor = operations.OperationAddTagInteractor(
            self._operations_repo, self._tags_repo
        )
        interactor.set_params(operation, payload['name'])
        tag = await interactor.execute()

        return {'tag': self.serialize(tag)}

    async def remove_tag(self, owner: Owner, account_pk, operation_pk, tag_pk):
        account = await self.fetch_account(owner, account_pk)
        operation = await self.fetch_operation(account, operation_pk)

        tag = await self._tags_repo.fetch_tag(owner, tag_pk)

        await self._operations_repo.remove_tag(operation, tag)
