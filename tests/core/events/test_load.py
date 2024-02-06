from datetime import datetime
from uuid import uuid4

import pytest

from tests.core.events.conftest import ComplexTestEvent, TestEvent, User
from wallet.core.events import Event, EventID, EventNotFound, InvalidEvent, Message


@pytest.mark.usefixtures("freezer")
def test_success(event_id: EventID) -> None:
    """Успешная десериализация события."""
    now = datetime.now().replace(microsecond=0)

    result = Event.load(
        message={
            "__data__": {
                "user_id": 123,
            },
            "__meta__": {
                "event_id": event_id.hex,
                "event_type": TestEvent.__event_type__,
                "version": TestEvent.__event_version__,
                "created_at": now.strftime("%Y-%m-%dT%H:%M:%S"),
            },
        }
    )

    assert result == TestEvent(user_id=123, event_id=event_id, event_created_at=now)


@pytest.mark.usefixtures("freezer")
def test_success_w_complex(event_id: EventID) -> None:
    """Успешная десериализация события c вложенными объектами."""
    now = datetime.now().replace(microsecond=0)

    result = Event.load(
        message={
            "__data__": {
                "owner": {
                    "id": 123,
                    "name": "john_doe",
                }
            },
            "__meta__": {
                "event_id": str(event_id),
                "event_type": ComplexTestEvent.__event_type__,
                "version": ComplexTestEvent.__event_version__,
                "created_at": now.strftime("%Y-%m-%dT%H:%M:%S"),
            },
        }
    )

    assert result == ComplexTestEvent(
        owner=User(id=123, name="john_doe"),
        event_id=event_id,
        event_created_at=now,
    )


@pytest.mark.parametrize(
    "message",
    [
        {
            "__data__": {"user_id": 123},
            "__meta__": {
                "event_id": uuid4().hex,
                "event_type": "test_event",
                "version": "2.0",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            },
        },
        {
            "__data__": {"user_id": 123},
            "__meta__": {
                "event_id": uuid4().hex,
                "event_type": "user_created",
                "version": "1.0",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            },
        },
    ],
)
def test_not_exist(message: Message) -> None:
    """Событие с таким типом не найдено."""
    with pytest.raises(EventNotFound):
        Event.load(message=message)


@pytest.mark.parametrize(
    "message",
    [
        {
            "__data__": {"user_id": 123},
        },
        {
            "__meta__": {
                "event_id": uuid4().hex,
                "event_type": "test_event",
                "version": "2.0",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            },
        },
        {
            "__data__": {"user_id": 123},
            "__meta__": {
                "event_id": uuid4().hex,
                "event_type": "test_event",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            },
        },
        {
            "__data__": {"user_id": 123},
            "__meta__": {
                "event_type": "test_event",
                "version": "2.0",
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            },
        },
        {
            "__data__": {"user_id": 123},
            "__meta__": {
                "event_id": uuid4().hex,
                "event_type": "test_event",
                "version": "2.0",
            },
        },
    ],
)
def test_invalid_event(message: Message) -> None:
    """Событие с некорректными данными."""
    with pytest.raises(InvalidEvent):
        Event.load(message=message)
