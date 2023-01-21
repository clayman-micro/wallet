from typing import Any, NamedTuple

import pkg_resources
import pytest
from aiohttp import web

from wallet.app import init


class Distribution(NamedTuple):
    """Application distribution."""

    project_name: str
    version: str


@pytest.fixture()
def distribution(monkeypatch: Any) -> None:
    """Patch application distribution."""

    def patch_distribution(*args: Any, **kwargs: Any) -> Distribution:
        return Distribution("wallet", "0.1.0")

    monkeypatch.setattr(pkg_resources, "get_distribution", patch_distribution)


@pytest.fixture()
def app(distribution: Distribution) -> web.Application:
    """Prepare test application."""
    return init("activity")
