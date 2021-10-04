from aiohttp import web
from jsonschema import validate
from marshmallow_jsonschema import JSONSchema

from wallet.web.schemas.abc import ResponseSchema


async def assert_response_conforms_to(response: web.Response, schema_cls: ResponseSchema) -> None:
    """Assert response conforms to schema.

    Args:
        response: HTTP web response.
        schema_cls: Schema class for response content validation.
    """
    if "application/json" in response.headers.get("Content-Type", ""):
        content = await response.json()
    else:
        content = await response.text()

    json_schema = JSONSchema()
    validate(instance=content, schema=json_schema.dump(schema_cls()))
