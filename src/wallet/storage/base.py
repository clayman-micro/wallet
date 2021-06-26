from abc import ABCMeta, abstractmethod

from databases import Database
from sqlalchemy.orm import Query  # type: ignore


class DBRepo(metaclass=ABCMeta):
    def __init__(self, database: Database):
        self._database = database

    @abstractmethod
    def _get_query(self, *args, **kwargs) -> Query:
        raise NotImplementedError()

    @abstractmethod
    def _process_row(self, row, *args, **kwargs):
        raise NotImplementedError()
