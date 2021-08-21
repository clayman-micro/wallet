from abc import ABCMeta, abstractmethod
from http import HTTPStatus
from typing import Any, Awaitable, Callable, Dict, Iterable, Optional, Tuple, Type, Union

from aiohttp import web
from aiohttp.web_response import json_response
from aiohttp_micro.web.handlers import get_payload
from aiohttp_micro.web.handlers.openapi import OpenAPISpec, ParameterIn, ParametersSchema, PayloadSchema, ResponseSchema
from marshmallow import Schema
from marshmallow.exceptions import ValidationError


Handler = Callable[
    [web.Response, Optional[Dict[str, Any]], Optional[Any]], Awaitable[Union[web.Response, Tuple[Any, HTTPStatus]]]
]
Responses = Dict[HTTPStatus, ResponseSchema]
Parameters = Optional[Dict[str, Type[ParametersSchema]]]
Payload = Optional[Type[PayloadSchema]]
Tags = Optional[Iterable[str]]


class InvalidParameters(Exception):
    def __init__(self, errors) -> None:
        self._errors = errors

    @property
    def errors(self):
        return self._errors


class InvalidPayload(Exception):
    def __init__(self, errors) -> None:
        self._errors = errors

    @property
    def errors(self):
        return self._errors


class OperationView(metaclass=ABCMeta):
    name: str
    responses: Responses
    tags: Tags

    parameters: Parameters = None
    payload_cls: Payload = None
    security: Optional[Any] = None

    def __init__(self, name: str, security: Any, tags: Tags) -> None:
        self.name = name
        self.security = security
        self.tags = tags

    @property
    def spec(self) -> OpenAPISpec:
        return OpenAPISpec(
            operation=self.name,
            parameters=self.parameters.values(),
            payload=self.payload_cls,
            responses=self.responses,
            security=self.security,
            tags=self.tags,
        )

    def get_parameters(self, request: web.Request) -> Dict[str, Any]:
        parameters = {}
        for section, schema_cls in self.parameters.items():
            schema = self.create_schema(schema_cls)

            if schema.in_ == ParameterIn.query:
                src = request.query
            elif schema.in_ == ParameterIn.header:
                src = request.headers
            elif schema.in_ == ParameterIn.path:
                src = request.match_info
            elif schema.in_ == ParameterIn.cookies:
                src = request.cookies

            try:
                parameters[section] = schema.load(src)
            except ValidationError as exc:
                raise InvalidParameters(errors=exc.messages)

        return parameters

    def create_schema(self, schema_cls: Type[Schema]) -> Schema:
        return schema_cls()

    async def get_payload(self, request: web.Request) -> None:
        raw_payload = await get_payload(request)

        try:
            schema = self.create_schema(self.payload_cls)
            return schema.load(raw_payload)
        except ValidationError as exc:
            raise InvalidPayload(errors=exc.errors)

    @abstractmethod
    async def process_request(
        self, request: web.Request, params: Optional[Dict[str, Any]] = None, payload: Optional[Payload] = None
    ) -> Union[web.Response, Tuple[Any, HTTPStatus]]:
        pass

    def process_response(self, response: Union[web.Response, Tuple[Any, HTTPStatus]]) -> web.Response:
        if not isinstance(response, web.Response):
            data, status = response

            schema_cls = self.responses.get(status, None)
            if not schema_cls:
                raise ValueError("Unsupported response status")

            schema = self.create_schema(schema_cls)
            response = json_response(schema.dump(data), status=status)

        return response

    async def handle(self, request: web.Request) -> web.Response:
        params = None
        if self.parameters:
            try:
                params = self.get_parameters(request)
            except InvalidParameters as exc:
                return self.process_response(response=(exc.errors, HTTPStatus.BAD_REQUEST))

        payload = None
        if self.payload_cls:
            try:
                payload = await self.get_payload(request)
            except InvalidPayload as exc:
                return self.process_response(response=(exc.errors, HTTPStatus.UNPROCESSABLE_ENTITY))

        response = await self.process_request(request=request, params=params, payload=payload)

        return self.process_response(response)
