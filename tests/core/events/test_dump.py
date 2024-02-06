from datetime import datetime

import pytest

from tests.core.events.conftest import (
    ComplexTestEvent,
    TestEvent,
    TestEventWithMeta,
    User,
)
from wallet.core.events import EventID, Message


@pytest.mark.usefixtures("freezer")
def test_success(event_id: EventID) -> None:
    """Успешная сериализация события."""
    event = TestEvent(user_id=123, event_id=event_id, event_created_at=datetime.now())

    result: Message = event.dump()

    assert result == {
        "__data__": {
            "user_id": 123,
        },
        "__meta__": {
            "event_id": event_id.hex,
            "event_type": TestEvent.__event_type__,
            "version": "1.0",
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        },
    }


@pytest.mark.usefixtures("freezer")
def test_success_w_custom_meta(event_id: EventID) -> None:
    """Успешная сериализация события c дополнительными метаданными."""
    event = TestEventWithMeta(
        user_id=123,
        event_id=event_id,
        event_created_at=datetime.now(),
    )

    result: Message = event.dump()

    assert result == {
        "__data__": {
            "user_id": 123,
        },
        "__meta__": {
            "event_id": event_id.hex,
            "event_type": TestEventWithMeta.__event_type__,
            "version": "1.1",
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        },
    }


@pytest.mark.usefixtures("freezer")
def test_success_w_complex(event_id: EventID) -> None:
    """Успешная сериализация события c вложенными объектами."""
    event = ComplexTestEvent(
        owner=User(id=123, name="john_doe"),
        event_id=event_id,
        event_created_at=datetime.now(),
    )

    result: Message = event.dump()

    assert result == {
        "__data__": {
            "owner": {
                "id": 123,
                "name": "john_doe",
            }
        },
        "__meta__": {
            "event_id": event_id.hex,
            "event_type": ComplexTestEvent.__event_type__,
            "version": "1.0",
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        },
    }
