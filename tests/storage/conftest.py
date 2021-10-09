from typing import Any

import pytest
from _pytest.fixtures import FixtureRequest
from passport.domain import User


@pytest.fixture(scope="module")
def owners(request: FixtureRequest, faker) -> dict[int, User]:
    """Prepare owners."""
    users: dict[int, User] = {}

    for item in request.param:
        user = User(key=item["key"], email=item.get("email", faker.free_email()))
        users[user.key] = user

    return users


@pytest.fixture(scope="function")
def owner(request: FixtureRequest, owners: dict[int, User]) -> User:
    """Choose owner."""
    return owners.get(request.param)


@pytest.fixture
def key(request) -> int:
    """Get instance key."""
    return request.param


@pytest.fixture
def name(request: FixtureRequest) -> str:
    """Get instance name."""
    return request.param


@pytest.fixture
def expected(request: FixtureRequest) -> Any:
    """Get expected test result."""
    return request.param
