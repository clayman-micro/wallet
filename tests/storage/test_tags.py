import pytest  # type: ignore

from tests.storage import prepare_tags
from wallet.domain import EntityAlreadyExist
from wallet.domain.entities import Tag
from wallet.domain.storage import TagQuery
from wallet.storage.tags import TagsDBRepo


@pytest.mark.integration
async def test_add_tag(fake, app, user):
    tag = Tag(0, fake.word(), user)

    async with app["db"].acquire() as conn:
        repo = TagsDBRepo(conn)
        key = await repo.add(tag)

        assert key == 1

        query = (
            "SELECT name FROM tags WHERE enabled = True AND user_id = $1 AND id = $2"
        )
        name = await conn.fetchval(query, user.key, key)

        assert name == tag.name


@pytest.mark.integration
async def test_add_tag_failed(fake, app, user):
    name = fake.word()

    async with app["db"].acquire() as conn:
        await prepare_tags(conn, [Tag(key=0, name=name, user=user)])

        with pytest.raises(EntityAlreadyExist):
            tag = Tag(0, name, user)

            repo = TagsDBRepo(conn)
            await repo.add(tag)


@pytest.mark.integration
async def test_find_account_by_key(fake, app, user):
    async with app["db"].acquire() as conn:
        repo = TagsDBRepo(conn)

        expected = await prepare_tags(
            conn,
            [
                Tag(key=0, name=fake.word(), user=user),
                Tag(key=0, name=fake.word(), user=user),
            ],
        )

        query = TagQuery(user, key=expected[0].key)
        tags = await repo.find(query)

        assert tags == [expected[0]]


@pytest.mark.integration
async def test_find_account_by_name(fake, app, user):
    async with app["db"].acquire() as conn:
        repo = TagsDBRepo(conn)

        expected = await prepare_tags(
            conn,
            [
                Tag(key=0, name=fake.word(), user=user),
                Tag(key=0, name=fake.word(), user=user),
            ],
        )

        query = TagQuery(user, name=expected[0].name)
        tags = await repo.find(query)

        assert tags == [expected[0]]


@pytest.mark.integration
async def test_rename_tag_name(fake, app, user):
    async with app["db"].acquire() as conn:
        tags = await prepare_tags(
            conn,
            [
                Tag(key=0, name=fake.word(), user=user),
                Tag(key=0, name=fake.word(), user=user),
            ],
        )

        tag = tags[0]
        tag.name = fake.word()

        repo = TagsDBRepo(conn)
        result = await repo.update(tag, fields=("name",))

        assert result is True

        query = (
            "SELECT name FROM tags WHERE enabled = TRUE AND user_id = $1 AND id = $2"
        )
        name = await conn.fetchval(query, user.key, tag.key)

        assert name == tag.name


@pytest.mark.integration
async def test_update_tag_duplicate_name(fake, app, user):
    async with app["db"].acquire() as conn:
        tags = await prepare_tags(
            conn,
            [
                Tag(key=0, name=fake.word(), user=user),
                Tag(key=0, name=fake.word(), user=user),
            ],
        )

        tag = tags[0]
        tag.name = tags[1].name

        repo = TagsDBRepo(conn)
        result = await repo.update(tag, fields=("name",))

        assert result is False


@pytest.mark.integration
async def test_remove_tag(fake, app, user):
    async with app["db"].acquire() as conn:
        tags = await prepare_tags(conn, [Tag(key=0, name=fake.word(), user=user)])

        repo = TagsDBRepo(conn)
        result = await repo.remove(tags[0])

        assert result is True

        query = "SELECT COUNT(id) FROM tags WHERE enabled = TRUE AND user_id = $1"
        count = await conn.fetchval(query, user.key)

        assert count == 0


@pytest.mark.integration
async def test_remove_tag_failed(fake, app, user):
    async with app["db"].acquire() as conn:
        tag = Tag(key=1, name=fake.word(), user=user)

        repo = TagsDBRepo(conn)
        result = await repo.remove(tag)

        assert result is False
