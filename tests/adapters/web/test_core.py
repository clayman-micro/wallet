import pytest  # type: ignore

from tests.adapters.web import assert_valid_response


@pytest.mark.integration
async def test_index(aiohttp_client, app, passport):
    app["passport"] = passport
    client = await aiohttp_client(app)
    access_token = "access-token"

    resp = await client.get("/", headers={"X-ACCESS-TOKEN": access_token})

    await assert_valid_response(
        resp,
        content_type="application/json; charset=utf-8",
        schema={
            "project": {"required": True, "type": "string"},
            "version": {"required": True, "type": "string"},
        },
    )
