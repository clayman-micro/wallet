from wallet.core.entities import Operation, OperationFilters
from wallet.core.storage.base import Repo


class OperationRepo(Repo[Operation, OperationFilters]):
    pass
