from asyncio import BaseEventLoop
from datetime import datetime

import pytest
from databases import Database
from passport.domain import User

from wallet.core.entities.accounts import Account
from wallet.storage.accounts import AccountDBRepo
from wallet.storage.accounts import accounts as accounts_table


@pytest.fixture
async def accounts(request, loop: BaseEventLoop, client, owners: dict[int, User]) -> list[Account]:
    """Prepare accounts in storage."""
    database: Database = client.app["db"]
    query = accounts_table.insert().returning(accounts_table.c.id)

    entities: list[Account] = []
    for item in request.param:
        owner = owners.get(item["owner"])
        account = Account(name=item["name"], user=owner)
        account.key = await database.execute(
            query,
            values={
                "name": account.name,
                "user": account.user.key,
                "enabled": item.get("enabled", False),
                "created_on": datetime.now(),
            },
        )

        entities.append(account)

    return entities


@pytest.fixture
def repo(client) -> AccountDBRepo:
    return AccountDBRepo(database=client.app["db"])
