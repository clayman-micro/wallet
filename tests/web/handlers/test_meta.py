import pytest
from aiohttp.test_utils import TestClient


@pytest.mark.smoke()
async def test_meta_endpoint(client: TestClient) -> None:
    """Successfully fetch application meta info."""
    resp = await client.get("/-/meta")

    assert resp.status == 200


@pytest.mark.smoke()
async def test_health_endpoint(client: TestClient) -> None:
    """Successfully fetch application health info."""
    resp = await client.get("/-/health")

    assert resp.status == 200


@pytest.mark.smoke()
async def test_metrics_endpoint(client: TestClient) -> None:
    """Successfully fetch application metrics."""
    resp = await client.get("/-/metrics")

    assert resp.status == 200
