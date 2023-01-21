from aiohttp.test_utils import TestClient


async def test_meta_endpoint(client: TestClient) -> None:
    """Successfully fetch application meta info."""
    resp = await client.get("/-/meta")

    assert resp.status == 200


async def test_health_endpoint(client: TestClient) -> None:
    """Successfully fetch application health info."""
    resp = await client.get("/-/health")

    assert resp.status == 200
