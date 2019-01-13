import pytest  # type: ignore

from tests.storage import prepare_accounts, prepare_operations, prepare_tags
from wallet.domain import Operation, Tag
from wallet.domain.storage import EntityAlreadyExist
from wallet.storage.operations import OperationsDBRepo


@pytest.mark.integration
async def test_add_operation(fake, today, app, account, operation):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])

        repo = OperationsDBRepo(conn)
        key = await repo.add(operation)

        assert key == 1


@pytest.mark.integration
async def test_add_operation_with_tags(fake, today, app, user, account, operation, tag):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])
        await prepare_tags(conn, [tag])

        operation.tags = [tag]

        repo = OperationsDBRepo(conn)
        key = await repo.add(operation)

        assert key == 1

        query = "SELECT COUNT(*) FROM operation_tags WHERE operation_id = $1"
        operation_tags = await conn.fetchval(query, key)

        assert operation_tags == 1


@pytest.mark.integration
async def test_find_operation_by_key(fake, app, account, operation):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])
        await prepare_operations(conn, [operation])

        repo = OperationsDBRepo(conn)
        result = await repo.find_by_key(account, key=operation.key)

        assert result == operation


@pytest.mark.integration
async def test_remove_operation(fake, app, account, operation):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])
        await prepare_operations(conn, [operation])

        repo = OperationsDBRepo(conn)
        result = await repo.remove(operation)

        assert result is True


@pytest.mark.integration
async def test_remove_operation_failed(fake, app, account, operation):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])

        operation.key = 1

        repo = OperationsDBRepo(conn)
        result = await repo.remove(operation)

        assert result is False


@pytest.mark.integration
async def test_add_tag_to_operation(fake, app, user, account, operation, tag):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])
        await prepare_operations(conn, [operation])
        await prepare_tags(conn, [tag])

        repo = OperationsDBRepo(conn)
        result = await repo.add_tag(operation, tag)

        assert result is True

        query = "SELECT COUNT(*) FROM operation_tags WHERE operation_id = $1 AND tag_id = $2"
        count = await conn.fetchval(query, operation.key, tag.key)

    assert count == 1


@pytest.mark.integration
async def test_add_existed_tag_to_operation(fake, app, user, account, operation, tag):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])
        await prepare_operations(conn, [operation])
        await prepare_tags(conn, [tag])

        await conn.execute("""
          INSERT INTO operation_tags (operation_id, tag_id) VALUES ($1, $2);
        """, operation.key, tag.key)

        with pytest.raises(EntityAlreadyExist):
            repo = OperationsDBRepo(conn)
            await repo.add_tag(operation, tag)


@pytest.mark.integration
async def test_remove_tag_from_operation(fake, app, user, account, operation, tag):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])
        await prepare_operations(conn, [operation])
        await prepare_tags(conn, [tag])

        await conn.execute("""
          INSERT INTO operation_tags (operation_id, tag_id) VALUES ($1, $2);
        """, operation.key, tag.key)

        repo = OperationsDBRepo(conn)
        result = await repo.remove_tag(operation, tag)

        assert result is True

        query = "SELECT COUNT(*) FROM operation_tags WHERE operation_id = $1 AND tag_id = $2"
        count = await conn.fetchval(query, operation.key, tag.key)

    assert count == 0
