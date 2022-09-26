from typing import NamedTuple

import pkg_resources  # type: ignore
import pytest  # type: ignore
from aiohttp import web

from wallet.app import init


@pytest.fixture(scope="function")
def distribution(monkeypatch):
    """Patch application distribution."""

    class Distribution(NamedTuple):
        project_name: str
        version: str

    def patch_distribution(*args, **kwargs):
        return Distribution("activity", "0.1.0")

    monkeypatch.setattr(pkg_resources, "get_distribution", patch_distribution)


@pytest.fixture(scope="function")
def app(distribution) -> web.Application:
    """Prepare test application."""
    app = init("activity")

    return app
