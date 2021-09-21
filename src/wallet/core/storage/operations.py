from wallet.core.entities import Operation, OperationFilters
from wallet.core.storage.abc import Repo


class OperationRepo(Repo[Operation, OperationFilters]):
    pass
