from typing import Dict, Optional

from wallet.entities import Account, Owner
from wallet.interactors import accounts
from wallet.repositories.accounts import AccountsRepository


Name = Optional[str]


class AccountsAPIAdapter(object):
    def __init__(self, repo: AccountsRepository, operations_repo=None) -> None:
        self.repo = repo
        self.operations_repo = operations_repo

    def serialize(self, account: Account) -> Dict:
        return {
            'id': account.pk,
            'name': account.name,
            'amount': account.amount
        }

    async def fetch(self, owner: Owner, filters=None) -> Dict:
        meta = {'total': 0}

        name = filters.name if filters else None
        if name:
            meta['filters'] = filters.to_dict()

        interactor = accounts.GetAccountsInteractor(self.repo)
        interactor.set_params(owner, name=name)

        items = await interactor.execute()
        meta['total'] = len(items)

        return {
            'accounts': [self.serialize(item) for item in items],
            'meta': meta
        }

    async def add_account(self, owner: Owner, payload: Dict) -> Dict:
        interactor = accounts.CreateAccountInteractor(self.repo)
        interactor.set_params(owner, payload['name'], payload.get('amount', 0))

        account = await interactor.execute()

        return {'account': self.serialize(account)}

    async def fetch_account(self, owner: Owner, pk: int) -> Dict:
        interactor = accounts.GetAccountInteractor(self.repo)
        interactor.set_params(owner, pk)

        account = await interactor.execute()

        return {'account': self.serialize(account)}

    async def update_account(self, owner: Owner, pk: int, payload) -> Dict:
        interactor = accounts.UpdateAccountInteractor(self.repo,
                                                      self.operations_repo)
        interactor.set_params(owner, pk, payload.get('name', None),
                              payload.get('original', None))

        account = await interactor.execute()

        return {'account': self.serialize(account)}

    async def remove_account(self, owner: Owner, pk: int) -> None:
        interactor = accounts.RemoveAccountInteractor(self.repo)
        interactor.set_params(owner, pk)

        await interactor.execute()
