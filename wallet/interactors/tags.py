from typing import List

from wallet.entities import EntityAlreadyExist, Owner, Tag
from wallet.repositories.tags import TagsRepository
from wallet.validation import ValidationError, Validator


schema = {
    'name': {
        'type': 'string', 'maxlength': 255, 'required': True, 'empty': False
    }
}


class FetchTagsInteractor(object):
    def __init__(self, repo: TagsRepository) -> None:
        self._repo = repo
        self._name = ''
        self._owner = None

    def set_params(self, owner: Owner, name: str = '') -> None:
        self._owner = owner
        self._name = name

    async def execute(self) -> List[Tag]:
        return await self._repo.fetch(owner=self._owner, name=self._name)


class FetchTagInteractor(object):
    def __init__(self, repo: TagsRepository) -> None:
        self._repo = repo
        self._pk = 0
        self._owner = None

    def set_params(self, owner: Owner, pk: int) -> None:
        self._owner = owner
        self._pk = pk

    async def execute(self) -> Tag:
        return await self._repo.fetch_tag(owner=self._owner, pk=self._pk)


class AddTagInteractor(object):
    def __init__(self, repo: TagsRepository) -> None:
        self._repo = repo
        self._owner = None
        self._name = ''

        self._validator = Validator(schema)

    def set_params(self, owner: Owner, name: str) -> None:
        self._owner = owner
        self._name = name

    async def execute(self) -> Tag:
        document = self._validator.validate_payload({
            'name': self._name
        })

        try:
            tag = Tag(document['name'], self._owner)
            tag.pk = await self._repo.save_tag(tag)
        except EntityAlreadyExist:
            raise ValidationError({'name': 'Already exist'})

        return tag


class UpdateTagInteractor(object):
    def __init__(self, repo: TagsRepository) -> None:
        self._repo = repo
        self._owner = None
        self._pk = 0
        self._payload = {}

        self._validator = Validator(schema)

    def set_params(self, owner: Owner, pk: int, payload=None) -> None:
        self._owner = owner
        self._pk = pk
        self._payload = payload

    async def execute(self) -> Tag:
        tag = await self._repo.fetch_tag(self._owner, self._pk)

        document = self._validator.validate_payload(self._payload, True)

        for key, value in iter(document.items()):
            setattr(tag, key, value)

        try:
            await self._repo.update_tag(tag, list(self._payload.keys()))
        except EntityAlreadyExist:
            raise ValidationError({'name': 'Already exist'})

        return tag


class RemoveTagInteractor(object):
    def __init__(self, repo: TagsRepository) -> None:
        self._repo = repo
        self._owner = None
        self._pk = 0

    def set_params(self, owner: Owner, pk: int) -> None:
        self._owner = owner
        self._pk = pk

    async def execute(self) -> bool:
        tag = await self._repo.fetch_tag(self._owner, self._pk)
        removed = await self._repo.remove_tag(tag)
        return removed
