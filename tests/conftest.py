import pkg_resources
import punq
import pytest
from aiohttp import web
from structlog.types import WrappedLogger

from wallet.app import create_container, init
from wallet.logging import configure_logging


@pytest.fixture(scope="session")
def distribution() -> pkg_resources.Distribution:
    """Patch application distribution."""
    return pkg_resources.get_distribution("wallet")


@pytest.fixture()
def logger(distribution: pkg_resources.Distribution) -> WrappedLogger:
    """Configure logging for tests."""
    return configure_logging(dist=distribution, debug=False)


@pytest.fixture()
def container(logger: WrappedLogger) -> punq.Container:
    """Create IoC container."""
    return create_container(logger=logger)


@pytest.fixture()
def app(distribution: pkg_resources.Distribution, container: punq.Container) -> web.Application:
    """Prepare test application."""
    return init(dist=distribution, container=container, debug=False)
