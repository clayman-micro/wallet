from abc import abstractmethod
from typing import Generic

from databases import Database
from sqlalchemy.orm import Query  # type: ignore

from wallet.core.entities.abc import EntityType, FiltersType


class DBRepo(Generic[EntityType, FiltersType]):
    def __init__(self, database: Database):
        self._database = database

    @abstractmethod
    def _get_query(self, filters: FiltersType) -> Query:
        ...

    @abstractmethod
    def _process_row(self, row, **kwargs) -> EntityType:
        ...
