from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict

from wallet.storage.owner import Owner


class AlreadyExist(Exception):
    pass


class ResourceNotFound(Exception):
    pass


class Resource(ABC):

    __slots__ = ('id', 'owner_id', 'enabled', 'created_on')

    def __init__(self, owner: Owner, **optional) -> None:
        self.owner_id = owner.id

        self.id = optional.get('id', 0)
        self.enabled = optional.get('enabled', True)

        created_on = optional.get('created_on', None)
        if not created_on:
            created_on = datetime.now()

        self.created_on = created_on

    @abstractmethod
    def serialize(self) -> Dict:
        return {'id': self.id}

    def update(self, **values) -> None:
        for key, value in iter(values.items()):
            if key in self.__slots__:
                setattr(self, key, value)
