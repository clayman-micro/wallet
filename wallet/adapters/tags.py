from wallet.entities import Owner, Tag
from wallet.interactors import tags


class TagsAPIAdapter(object):
    def __init__(self, repo) -> None:
        self._repo = repo

    def serialize(self, tag: Tag):
        return {
            'id': tag.pk,
            'name': tag.name
        }

    async def fetch(self, owner: Owner, filters=None):
        name = filters.name if filters else None

        interactor = tags.FetchTagsInteractor(self._repo)
        interactor.set_params(owner, name)
        items = await interactor.execute()

        result = {
            'tags': [self.serialize(item) for item in items],
            'meta': {
                'total': len(items)
            }
        }

        if name:
            result['meta']['filters'] = filters.to_dict()

        return result

    async def add_tag(self, owner: Owner, payload):
        interactor = tags.AddTagInteractor(repo=self._repo)
        interactor.set_params(owner, payload.get('name', None))
        tag = await interactor.execute()
        return {'tag': self.serialize(tag)}

    async def fetch_tag(self, owner: Owner, pk: int):
        interactor = tags.FetchTagInteractor(repo=self._repo)
        interactor.set_params(owner, pk)
        tag = await interactor.execute()
        return {'tag': self.serialize(tag)}

    async def update_tag(self, owner: Owner, pk: int, payload):
        interactor = tags.UpdateTagInteractor(repo=self._repo)
        interactor.set_params(owner, pk, payload)
        tag = await interactor.execute()
        return {'tag': self.serialize(tag)}

    async def remove_tag(self, owner: Owner, pk: int) -> None:
        interactor = tags.RemoveTagInteractor(repo=self._repo)
        interactor.set_params(owner, pk)
        await interactor.execute()
