from databases import Database

from wallet.core.storage import Storage
from wallet.storage.accounts import AccountDBRepo


class DBStorage(Storage):
    def __init__(self, database: Database) -> None:
        self.accounts = AccountDBRepo(database=database)
