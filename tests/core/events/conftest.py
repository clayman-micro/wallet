from typing import Any
from uuid import uuid4

import attrs
import pytest

from wallet.core.events import Event, EventID


@pytest.fixture()
def event_id() -> EventID:
    """Идентификатор события."""
    return EventID(uuid4())


@attrs.frozen(kw_only=True)
class TestEvent(Event):
    """Тестовое событие."""

    user_id: int


@attrs.frozen(kw_only=True)
class TestEventWithMeta(Event):
    """Тестовое событие с дополнительными метаданными."""

    user_id: int

    class Meta:
        """Метаданные события."""

        event_type: str = "test_event"
        version: str = "1.1"


@attrs.define(kw_only=True)
class User:
    """Сущность пользователя."""

    id: int
    name: str

    @classmethod
    def load(cls, value: dict[str, Any]) -> "User":
        """Десериализация пользователя."""
        if isinstance(value, dict):
            return cls(**value)

        return value


@attrs.frozen(kw_only=True)
class ComplexTestEvent(Event):
    """Тестовое событие с вложенными объектом."""

    owner: User = attrs.field(converter=User.load)  # type: ignore

    class Meta:
        """Метаданные события."""

        event_type: str = "complex_event"
