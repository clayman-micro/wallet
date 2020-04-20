import pytest  # type: ignore

from tests.storage import prepare_accounts, prepare_operations, prepare_tags
from wallet.domain import Tag
from wallet.domain.storage import EntityAlreadyExist
from wallet.storage.tags import TagsDBRepo


@pytest.mark.integration
async def test_add_tag(fake, app, user, tag):
    async with app["db"].acquire() as conn:
        repo = TagsDBRepo(conn)
        key = await repo.add(tag)

        assert key == 1

        query = "SELECT name FROM tags WHERE enabled = True AND user_id = $1 AND id = $2"
        name = await conn.fetchval(query, user.key, key)

        assert name == tag.name


@pytest.mark.integration
async def test_add_tag_failed(fake, app, user, tag):
    name = fake.word()
    tag.name = name

    async with app["db"].acquire() as conn:
        await prepare_tags(conn, [tag])

        with pytest.raises(EntityAlreadyExist):
            tag = Tag(0, name, user)

            repo = TagsDBRepo(conn)
            await repo.add(tag)


@pytest.mark.integration
async def test_find_tag_by_key(fake, app, user, tag):
    async with app["db"].acquire() as conn:
        await prepare_tags(conn, [tag])

        repo = TagsDBRepo(conn)
        result = await repo.find_by_key(user, key=tag.key)

        assert result == tag


@pytest.mark.integration
async def test_find_tag_by_name(fake, app, user, tag):
    async with app["db"].acquire() as conn:
        await prepare_tags(conn, [tag])

        repo = TagsDBRepo(conn)
        result = await repo.find_by_name(user, name=tag.name)

        assert result == [tag]


@pytest.mark.integration
async def test_find_tags_by_operations(
    fake, app, user, account, operation, tag
):
    async with app["db"].acquire() as conn:
        await prepare_accounts(conn, [account])
        await prepare_operations(conn, [operation])
        await prepare_tags(conn, [tag])

        await conn.execute(
            """
          INSERT INTO operation_tags (operation_id, tag_id) VALUES ($1, $2);
        """,
            operation.key,
            tag.key,
        )

        repo = TagsDBRepo(conn)
        tags = await repo.find_by_operations(user, (operation.key,))

        assert tags == {operation.key: [tag]}


@pytest.mark.integration
async def test_rename_tag_name(fake, app, user, tag):
    async with app["db"].acquire() as conn:
        await prepare_tags(conn, [tag])

        tag.name = fake.word()

        repo = TagsDBRepo(conn)
        result = await repo.update(tag, fields=("name",))

        assert result is True

        query = "SELECT name FROM tags WHERE enabled = TRUE AND user_id = $1 AND id = $2"
        name = await conn.fetchval(query, user.key, tag.key)

        assert name == tag.name


@pytest.mark.integration
async def test_update_tag_duplicate_name(fake, app, user, tag):
    another_tag = Tag(key=0, name=fake.word(), user=user)

    async with app["db"].acquire() as conn:
        await prepare_tags(conn, [tag, another_tag])

        tag.name = another_tag.name

        repo = TagsDBRepo(conn)
        result = await repo.update(tag, fields=("name",))

        assert result is False


@pytest.mark.integration
async def test_remove_tag(fake, app, user, tag):
    async with app["db"].acquire() as conn:
        await prepare_tags(conn, [tag])

        repo = TagsDBRepo(conn)
        result = await repo.remove(tag)

        assert result is True

        query = (
            "SELECT COUNT(id) FROM tags WHERE enabled = TRUE AND user_id = $1"
        )
        count = await conn.fetchval(query, user.key)

        assert count == 0


@pytest.mark.integration
async def test_remove_tag_failed(fake, app, user, tag):
    async with app["db"].acquire() as conn:
        tag.key = 1

        repo = TagsDBRepo(conn)
        result = await repo.remove(tag)

        assert result is False
