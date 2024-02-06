from __future__ import annotations

from abc import ABCMeta
from datetime import datetime
from typing import Any, ClassVar, NewType, Type, TypeVar, cast
from uuid import UUID, uuid4

import attrs
import jsonschema
from inflection import underscore

Message = dict[str, Any]
EventID = NewType("EventID", UUID)
ET = TypeVar("ET")


@attrs.define(kw_only=True, slots=True)
class BaseEventException(Exception):
    """Базовая ошибка, связанная с событиями."""

    message: str


@attrs.define(kw_only=True, slots=True)
class InvalidEvent(BaseEventException):
    """Неправильный формат события."""


@attrs.define(kw_only=True, slots=True)
class EventNotFound(BaseEventException):
    """Событие не найдено."""


@attrs.define(kw_only=True, slots=True)
class EventAlreadyExist(BaseEventException):
    """Событие такого типа уже существует."""


meta_schema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "event_id": {"type": "string"},
        "event_type": {"type": "string"},
        "version": {"type": "string"},
        "created_at": {"type": "string"},
    },
    "required": ["event_id", "event_type", "version", "created_at"],
}


@attrs.frozen(kw_only=True, slots=True)
class EventMeta(object):
    """Метаданные события."""

    event_id: EventID = attrs.field(factory=lambda: EventID(uuid4()))
    event_type: str = attrs.field()
    version: str = attrs.field(default="1.0")
    created_at: datetime = attrs.field(factory=datetime.now)


class BaseEvent(ABCMeta):
    """Базовый класс события."""

    registry: dict[tuple[str, str], BaseEvent] | None = None

    __event_type__: ClassVar[str]
    __event_version__: ClassVar[str] = "1.0"
    __event_schema__: ClassVar[dict[str, Any]]

    def __new__(
        cls: Type[BaseEvent],
        name: str,
        bases: tuple[type, ...],
        attributes: dict[str, Any],
    ) -> BaseEvent:
        """Cоздание нового класса для описания события.

        Args:
            name: Имя класса.
            bases: Список родительских классов.
            attributes: Аттрибуты класса.

        Returns:
            Класс
        """
        event_type = underscore(name)
        version = "1.0"
        event_schema: dict[str, Any] = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "__data__": {"type": "object"},
                "__meta__": meta_schema,
            },
            "required": ["__data__", "__meta__"],
        }

        meta = attributes.get("Meta")
        if meta:
            event_type = getattr(meta, "event_type", event_type)
            version = getattr(meta, "version", version)
            event_schema = getattr(meta, "schema", event_schema)

        attributes.update(
            {
                "__event_type__": event_type,
                "__event_version__": version,
                "__event_schema__": event_schema,
            }
        )

        event_cls = super(BaseEvent, cls).__new__(cls, name, bases, attributes)

        if "__attrs_attrs__" in attributes:
            cls.register_event_cls(event_cls)

        return event_cls

    @classmethod
    def register_event_cls(cls, event_cls: BaseEvent) -> None:
        """Регистрация нового типа события."""
        if not cls.registry:  # pragma: no cover
            cls.registry = {}

        key = (event_cls.__event_type__, event_cls.__event_version__)

        if key in cls.registry:
            raise EventAlreadyExist(
                message=f"Event `{event_cls.__event_type__}` of "
                f"version `{event_cls.__event_version__}` already exist"
            )

        cls.registry[key] = event_cls

    @classmethod
    def resolve_event_cls(cls, event_type: str, version: str) -> BaseEvent:
        """Получение класса события по типу и версии."""
        if not cls.registry:  # pragma: no cover
            cls.registry = {}

        try:
            return cls.registry[(event_type, version)]
        except KeyError:
            raise EventNotFound(
                message=f"Event `{event_type}` of version `{version}` already exist"
            )


def dump_filter(attr: attrs.Attribute[Any], value: Any) -> bool:
    """Фильтр для определения какие поля нужно сериализовать."""
    is_dump = attr.metadata.get("dump", None)

    if is_dump is not None:
        return bool(is_dump)

    return True


def str_to_uuid(value: str | UUID) -> UUID:
    """Преобразование строки в UUID."""
    if isinstance(value, UUID):
        return value

    return UUID(hex=value)


def str_to_datetime(value: str | datetime) -> datetime:
    """Преобразование строки в datetime."""
    if isinstance(value, datetime):
        return value

    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")


@attrs.frozen(kw_only=True)
class Event(metaclass=BaseEvent):
    """Базовый класс события."""

    __event_type__: ClassVar[str]
    __event_version__: ClassVar[str]
    __event_schema__: ClassVar[dict[str, Any]]

    _event_id: EventID = attrs.field(
        alias="event_id",
        factory=lambda: EventID(uuid4()),
        converter=str_to_uuid,
        metadata={"dump": False},
    )
    _event_created_at: datetime = attrs.field(
        alias="event_created_at",
        factory=datetime.now,
        converter=str_to_datetime,
        metadata={"dump": False},
    )

    __event_meta__: EventMeta = attrs.field(init=False, metadata={"dump": False})

    @__event_meta__.default
    def _(self) -> EventMeta:
        return EventMeta(
            event_id=self._event_id,
            event_type=self.__event_type__,
            version=self.__event_version__,
            created_at=self._event_created_at,
        )

    @classmethod
    def validate(cls, message: Message) -> None:
        """Проверка события по схеме.

        Args:
            message: Сериализованное представление события.

        Raises:
            InvalidEvent: Некорректное событие.
        """
        try:
            jsonschema.validate(instance=message, schema=cls.__event_schema__)
        except jsonschema.ValidationError as exc:
            raise InvalidEvent(message=exc.message)

    @classmethod
    def load(cls, message: Message) -> Event:
        """Десериализация события.

        Args:
            message: Сериализованное представление события.

        Returns:
            Объект события.
        """
        cls.validate(message)

        event_meta = message.get("__meta__")
        event_data: dict[str, Any] | None = message.get("__data__")

        if event_data and event_meta:
            event_type = event_meta.get("event_type")
            version = event_meta.get("version")

            event_cls = cast(
                Type[Event],
                BaseEvent.resolve_event_cls(event_type=event_type, version=version),
            )

            return event_cls(
                **event_data,
                event_id=event_meta.get("event_id"),
                event_created_at=event_meta.get("created_at"),
            )

        raise InvalidEvent(message="Invalid event")

    def dump_metadata(self) -> dict[str, str]:
        """Сериализация метаданных события.

        Returns:
            Сериализованное представление метаданных события.
        """
        return {
            "event_id": self.__event_meta__.event_id.hex,
            "event_type": self.__event_meta__.event_type,
            "version": self.__event_meta__.version,
            "created_at": self.__event_meta__.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        }

    def dump(self) -> Message:
        """Сериализация события.

        Returns:
            Сериализованное представление.
        """
        return {
            "__data__": attrs.asdict(self, filter=dump_filter),
            "__meta__": self.dump_metadata(),
        }
